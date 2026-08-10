# Canonical sources per topic

Explainers must cite the studied paper AND the relevant canonical sources below,
with equation/section numbers. Grow this list with every distilled paper.

## Flow matching
- Lipman et al., *Flow Matching for Generative Modeling*, ICLR 2023 — arXiv:2210.02747
- Lipman et al., *Flow Matching Guide and Code* (Meta), 2024 — arXiv:2412.06264
- Liu et al., *Rectified Flow*, 2022 — arXiv:2209.03003 (straight-path/OT view)
- Albergo & Vanden-Eijnden, *Stochastic Interpolants*, 2023 — arXiv:2303.08797

## Diffusion models (background for AR-diffusion)
- Ho et al., *DDPM*, 2020 — arXiv:2006.11239
- Song et al., *Score-Based Generative Modeling through SDEs*, ICLR 2021 — arXiv:2011.13456

## Diffusion transformers
- Peebles & Xie, *Scalable Diffusion Models with Transformers (DiT)*, ICCV 2023 — arXiv:2212.09748
- Esser et al., *SD3 / MMDiT*, 2024 — arXiv:2403.03206
- Black Forest Labs, *Flux* — github.com/black-forest-labs/flux (dual/single-stream reference impl.)
- Su et al., *RoPE*, 2021 — arXiv:2104.09864

## Latent generative modeling
- Rombach et al., *Latent Diffusion (LDM)*, CVPR 2022 — arXiv:2112.10752
- Chen et al., *DCAE (Deep Compression AE)*, 2024 — arXiv:2410.10733
- van den Oord et al., *VQ-VAE*, 2017 — arXiv:1711.00937 (discrete contrast)

## World models / driving (context for Epona)
- Ha & Schmidhuber, *World Models*, 2018 — arXiv:1803.10122
- Hu et al., *GAIA-1*, 2023 — arXiv:2309.17080
- Gao et al., *Vista*, 2024 — arXiv:2405.17398 (joint video-diffusion contrast)
- Chen et al., *Diffusion Forcing*, 2024 — arXiv:2407.01392

## Exposure bias / AR drift
- Bengio et al., *Scheduled Sampling*, 2015 — arXiv:1506.03099
- Valevski et al., *GameNGen*, 2024 — arXiv:2408.14837 (noise augmentation)
- Hu et al., *DrivingWorld*, 2024 — arXiv:2412.19505 (token dropout)

## Volumetric rendering / radiance fields (3DGS campaign)
- Max, *Optical Models for Direct Volume Rendering*, IEEE TVCG 1995 (transmittance derivation)
- Mildenhall et al., *NeRF*, ECCV 2020 — arXiv:2003.08934
- Tagliasacchi & Barron, *NeRF representation digest*, 2022 — arXiv:2209.02417 (clean discretization)
- Barron et al., *Mip-NeRF360*, CVPR 2022 — arXiv:2111.12077 (quality baseline in 3DGS tables)
- Müller et al., *InstantNGP*, SIGGRAPH 2022 — arXiv:2201.05989 (speed baseline)
- Fridovich-Keil et al., *Plenoxels*, CVPR 2022 — arXiv:2112.05131 (SH-on-voxels precedent)

## Gaussian splatting
- Kerbl et al., *3D Gaussian Splatting for Real-Time Radiance Field Rendering*, SIGGRAPH 2023 — arXiv:2308.04079
- Zwicker et al., *EWA Volume Splatting*, IEEE VIS 2001 (+ *EWA Splatting*, TVCG 2002) — the eq-5 projection math
- Lassner & Zollhöfer, *Pulsar*, CVPR 2021 — arXiv:2004.07484 (tile/sphere rasterization precursor)
- Ye et al., *gsplat: An Open-Source Library for Gaussian Splatting*, 2024 — arXiv:2409.06765 (modern kernel/Jacobian restatement)
- Yu et al., *Mip-Splatting*, CVPR 2024 — arXiv:2311.16493 (fixes the 0.3-dilation aliasing; future campaign)

## Spherical harmonics
- Green, *Spherical Harmonic Lighting: The Gritty Details*, GDC 2003
- Ramamoorthi & Hanrahan, *An Efficient Representation for Irradiance Environment Maps*, SIGGRAPH 2001
- Sloan, *Stupid Spherical Harmonics Tricks*, GDC 2008 (real-SH conventions/constants)

## Attention / video transformers
- Arnab et al., *ViViT*, 2021 — arXiv:2103.15691 (factorized spatiotemporal attention)
- Blattmann et al., *Align Your Latents*, 2023 — arXiv:2304.08818 (temporal layers in video LDMs)
