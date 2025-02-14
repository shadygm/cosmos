import numpy as np
from plyfile import PlyData
from dataclasses import dataclass

@dataclass
class GaussianData:
    xyz: np.ndarray      # shape: (N, 3)
    rot: np.ndarray      # shape: (N, 4)
    scale: np.ndarray    # shape: (N, 3)
    opacity: np.ndarray  # shape: (N, 1)
    sh: np.ndarray       # shape: (N, sh_dim)

    def flat(self) -> np.ndarray:
        """
        Returns a contiguous 2D array (N x total_dims) where each row is the concatenation of:
          [xyz, rot, scale, opacity, sh]
        """
        ret = np.concatenate([self.xyz, self.rot, self.scale, self.opacity, self.sh], axis=-1)
        return np.ascontiguousarray(ret)
    
    def __len__(self) -> int:
        return len(self.xyz)
    
    @property 
    def sh_dim(self) -> int:
        return self.sh.shape[-1]


def naive_gaussian():
    """
    Creates a set of 4 naive Gaussians with hard-coded values.
    """
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
        1, 0, 0, 0,
    ], dtype=np.float32).reshape(-1, 4)

    gau_scale = np.array([
        0.03, 0.03, 0.03,
        0.2,  0.03, 0.03,
        0.03, 0.2,  0.03,
        0.03, 0.03, 0.2,
    ], dtype=np.float32).reshape(-1, 3)

    gau_opacity = np.array([
        1, 1, 1, 1,
    ], dtype=np.float32).reshape(-1, 1)

    gau_sh = np.array([
        1, 0, 1,
        1, 0, 0,
        0, 1, 0,
        0, 0, 1,
    ], dtype=np.float32).reshape(-1, 3)
    # Normalize the spherical-harmonics coefficients as in the reference.
    gau_sh = (gau_sh - 0.5) / 0.28209

    return GaussianData(gau_xyz, gau_rot, gau_scale, gau_opacity, gau_sh)


def from_ply(path: str) -> GaussianData:
    """
    Loads Gaussians from a PLY file and returns a GaussianData instance.
    This implementation follows the reference structure.
    """
    max_sh_degree = 3
    plydata = PlyData.read(path)
    
    # Load positions.
    xyz = np.stack((
        np.asarray(plydata.elements[0]["x"]),
        np.asarray(plydata.elements[0]["y"]),
        np.asarray(plydata.elements[0]["z"])
    ), axis=1).astype(np.float32)
    
    # Load opacities and apply a sigmoid.
    opacities = np.asarray(plydata.elements[0]["opacity"])[..., np.newaxis].astype(np.float32)
    opacities = 1 / (1 + np.exp(-opacities))
    
    # Load direct current (DC) features for spherical harmonics.
    features_dc = np.zeros((xyz.shape[0], 3, 1), dtype=np.float32)
    features_dc[:, 0, 0] = np.asarray(plydata.elements[0]["f_dc_0"])
    features_dc[:, 1, 0] = np.asarray(plydata.elements[0]["f_dc_1"])
    features_dc[:, 2, 0] = np.asarray(plydata.elements[0]["f_dc_2"])
    
    # Load extra SH features.
    extra_f_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("f_rest_")]
    extra_f_names = sorted(extra_f_names, key=lambda x: int(x.split('_')[-1]))
    assert len(extra_f_names) == 3 * (max_sh_degree + 1) ** 2 - 3, "Unexpected number of extra features"
    features_extra = np.zeros((xyz.shape[0], len(extra_f_names)), dtype=np.float32)
    for idx, attr_name in enumerate(extra_f_names):
        features_extra[:, idx] = np.asarray(plydata.elements[0][attr_name])
    # Reshape and transpose to form proper SH coefficients (excluding DC).
    features_extra = features_extra.reshape((features_extra.shape[0], 3, (max_sh_degree + 1) ** 2 - 1))
    features_extra = np.transpose(features_extra, [0, 2, 1])
    
    # Load scales.
    scale_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("scale_")]
    scale_names = sorted(scale_names, key=lambda x: int(x.split('_')[-1]))
    scales = np.zeros((xyz.shape[0], len(scale_names)), dtype=np.float32)
    for idx, attr_name in enumerate(scale_names):
        scales[:, idx] = np.asarray(plydata.elements[0][attr_name])
    scales = np.exp(scales).astype(np.float32)
    
    # Load rotations.
    rot_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("rot")]
    rot_names = sorted(rot_names, key=lambda x: int(x.split('_')[-1]))
    rots = np.zeros((xyz.shape[0], len(rot_names)), dtype=np.float32)
    for idx, attr_name in enumerate(rot_names):
        rots[:, idx] = np.asarray(plydata.elements[0][attr_name])
    # Normalize rotations (assumed to be quaternions).
    rots = rots / np.linalg.norm(rots, axis=-1, keepdims=True)
    rots = rots.astype(np.float32)
    
    # Concatenate DC and extra features to form SH coefficients.
    sh = np.concatenate([
        features_dc.reshape(-1, 3),
        features_extra.reshape(xyz.shape[0], -1)
    ], axis=-1).astype(np.float32)
    
    return GaussianData(xyz, rots, scales, opacities, sh)


# --- Testing the implementation ---
if __name__ == "__main__":
    # Test naive gaussians.
    naive = naive_gaussian()
    print("Naive gaussians flat shape:", naive.flat().shape)
    
    # Test loading from a PLY file.
    # Replace the path below with a valid PLY file on your system.
    # ply_path = "/path/to/your/file.ply"
    # gs = load_ply(ply_path)
    # print("Loaded", len(gs), "gaussians with flat shape:", gs.flat().shape)
