import numpy as np
from plyfile import PlyData
from dataclasses import dataclass
from typing import List
import util

@dataclass
class Gaussian:
    xyz: np.ndarray     # shape: (3,)
    rot: np.ndarray     # shape: (4,)
    scale: np.ndarray   # shape: (3,)
    opacity: float      # a scalar value
    sh: np.ndarray      # shape: (3,) for the naive example (could be larger)

    def flat(self) -> np.ndarray:
        """
        Returns a 1D array concatenating all properties.
        """
        # Convert opacity to a one-element array so that all parts can be concatenated.
        return np.concatenate([self.xyz, self.rot, self.scale, np.array([self.opacity]), self.sh])
    
    @classmethod
    def naive_gaussians(cls) -> List['Gaussian']:
        """
        Creates a list of naive Gaussians based on hard-coded values.
        In this example, we create 4 Gaussians.
        """
        # Define batched arrays (each row corresponds to one Gaussian)
        gau_xyz = np.array([
            0, 0, 0,
            1, 0, 0,
            0, 1, 0,
            0, 0, 1,
        ], dtype=np.float32).reshape(-1, 3)

        gau_rot = np.array([
            1, 0, 0, 0,
            1, 0, 0, 0,
            1, 0, 0, 0,
            1, 0, 0, 0
        ], dtype=np.float32).reshape(-1, 4)

        gau_scale = np.array([
            0.03, 0.03, 0.03,
            0.2,  0.03, 0.03,
            0.03, 0.2,  0.03,
            0.03, 0.03, 0.2
        ], dtype=np.float32).reshape(-1, 3)

        gau_opacity = np.array([
            1, 1, 1, 1
        ], dtype=np.float32).reshape(-1, 1)

        gau_sh = np.array([
            1, 0, 1, 
            1, 0, 0, 
            0, 1, 0, 
            0, 0, 1, 
        ], dtype=np.float32).reshape(-1, 3)
        # Normalize the spherical-harmonics coefficients
        gau_sh = (gau_sh - 0.5) / 0.28209

        gaussians = []
        n = gau_xyz.shape[0]
        for i in range(n):
            gaussians.append(cls(
                xyz=gau_xyz[i],
                rot=gau_rot[i],
                scale=gau_scale[i],
                opacity=float(gau_opacity[i, 0]),
                sh=gau_sh[i]
            ))
        return gaussians

class GaussianSet:
    def __init__(self, gaussians: List[Gaussian]):
        self.gaussians = gaussians
        self.log = util.get_logger()

    def flat(self) -> np.ndarray:
        """
        Returns a 2D array where each row is the flattened representation of a single Gaussian.
        """
        xyz = np.stack([g.xyz for g in self.gaussians], axis=0)
        rot = np.stack([g.rot for g in self.gaussians], axis=0)
        scale = np.stack([g.scale for g in self.gaussians], axis=0)
        # Ensure opacity is a column vector (shape: (N, 1)) before concatenation.
        opacity = np.array([g.opacity for g in self.gaussians]).reshape(-1, 1)
        sh = np.stack([g.sh for g in self.gaussians], axis=0)
        
        ret = np.concatenate([xyz, rot, scale, opacity, sh], axis=-1)
        return np.ascontiguousarray(ret)
    
    def __len__(self) -> int:
        return len(self.gaussians)

    def append(self, item):
        """
        Appends either a single Gaussian or all Gaussians from another GaussianSet.

        Parameters:
            item (Gaussian or GaussianSet): The item(s) to append.
        """
        if isinstance(item, Gaussian):
            self.gaussians.append(item)
        elif isinstance(item, GaussianSet):
            self.gaussians.extend(item.gaussians)
        else:
            raise TypeError(f"append() expects a Gaussian or GaussianSet, got {type(item)}")

    @property
    def xyz(self) -> np.ndarray:
        """
        Returns a 2D array with the positions of all Gaussians.
        """
        return np.stack([g.xyz for g in self.gaussians], axis=0)

    @property
    def sh_dim(self) -> int:
        return self.gaussians[0].sh.shape[0] if self.gaussians else 0

    @classmethod
    def from_ply(cls, path: str) -> 'GaussianSet':
        """
        Loads a set of Gaussians from a PLY file.
        This method follows the structure of your original `load_ply` function.
        """
        max_sh_degree = 3
        plydata = PlyData.read(path)

        # Load positions
        xyz = np.stack((
            np.asarray(plydata.elements[0]["x"]),
            np.asarray(plydata.elements[0]["y"]),
            np.asarray(plydata.elements[0]["z"])
        ), axis=1).astype(np.float32)

        # Load opacities and apply a sigmoid
        opacities = np.asarray(plydata.elements[0]["opacity"])[..., np.newaxis].astype(np.float32)
        opacities = 1 / (1 + np.exp(-opacities))

        # Load DC (direct current) features for spherical harmonics
        features_dc = np.zeros((xyz.shape[0], 3, 1), dtype=np.float32)
        features_dc[:, 0, 0] = np.asarray(plydata.elements[0]["f_dc_0"])
        features_dc[:, 1, 0] = np.asarray(plydata.elements[0]["f_dc_1"])
        features_dc[:, 2, 0] = np.asarray(plydata.elements[0]["f_dc_2"])

        # Load extra features (assumed to be related to spherical harmonics)
        extra_f_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("f_rest_")]
        extra_f_names = sorted(extra_f_names, key=lambda x: int(x.split('_')[-1]))
        assert len(extra_f_names) == 3 * (max_sh_degree + 1) ** 2 - 3, "Unexpected number of extra features"
        features_extra = np.zeros((xyz.shape[0], len(extra_f_names)), dtype=np.float32)
        for idx, attr_name in enumerate(extra_f_names):
            features_extra[:, idx] = np.asarray(plydata.elements[0][attr_name])
        # Reshape and transpose to get proper SH coefficients (excluding DC)
        features_extra = features_extra.reshape((features_extra.shape[0], 3, (max_sh_degree + 1) ** 2 - 1))
        features_extra = np.transpose(features_extra, [0, 2, 1])

        # Load scales
        scale_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("scale_")]
        scale_names = sorted(scale_names, key=lambda x: int(x.split('_')[-1]))
        scales = np.zeros((xyz.shape[0], len(scale_names)), dtype=np.float32)
        for idx, attr_name in enumerate(scale_names):
            scales[:, idx] = np.asarray(plydata.elements[0][attr_name])
        scales = np.exp(scales).astype(np.float32)

        # Load rotations
        rot_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("rot")]
        rot_names = sorted(rot_names, key=lambda x: int(x.split('_')[-1]))
        rots = np.zeros((xyz.shape[0], len(rot_names)), dtype=np.float32)
        for idx, attr_name in enumerate(rot_names):
            rots[:, idx] = np.asarray(plydata.elements[0][attr_name])
        # Normalize rotations (assumed to be quaternions)
        rots = rots / np.linalg.norm(rots, axis=-1, keepdims=True)
        rots = rots.astype(np.float32)

        # Concatenate DC and extra features to form SH coefficients
        shs = np.concatenate([
            features_dc.reshape(-1, 3), 
            features_extra.reshape(xyz.shape[0], -1)
        ], axis=-1).astype(np.float32)

        # Create one Gaussian per point in the PLY file.
        gaussians = []
        n = xyz.shape[0]
        for i in range(n):
            # Here we assume:
            # - rots[i] has the expected shape (e.g. (4,))
            # - scales[i] has the expected shape (e.g. (3,))
            # - opacities[i] is a 1-element array (we convert it to float)
            # - shs[i] holds the SH coefficients for that Gaussian.
            gaussians.append(Gaussian(
                xyz=xyz[i],
                rot=rots[i],
                scale=scales[i],
                opacity=float(opacities[i, 0]),
                sh=shs[i]
            ))


        util.get_logger().info(f"Loaded {n} Gaussians from {path}")
        return cls(gaussians)


if __name__ == "__main__":
    # Useful to test if the loading works as appropriate
    path = "/home/shadygm/projects/uni/asig/dataset/ply/bonsai/point_cloud/iteration_30000/point_cloud.ply"
    gaussian_set = GaussianSet.from_ply(path)
    print(f"Loaded {len(gaussian_set)} Gaussians")
    a = gaussian_set.flat()
    print(a.shape)
