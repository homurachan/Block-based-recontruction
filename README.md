# Block-based-recontruction
Scripts and sources of the block-based reconstruction/refinement.

These scripts and codes are under WTFPL verion 2 license, a GPL-campatible free license.

The modification version of RELION is under the same license of RELION, which is GPL ver.2.

Please cite our paper: NATURE COMMUNICATIONS (2018) 9:1552 or DOI: 10.1038/s41467-018-04051-9
if our block-based reconstruction idea or these codes work.

# Updated 03.11.2025

Upload read_star_shift_crop_and_generate_new_star_v3.py . This python script can crop sub-particles directly from particle star. So no micrograph is needed if you don't have.

Python lib requirement: starfile, mrcfile, numpy.

Usage: `python read_star_shift_crop_and_generate_new_star_v3.py --star_name INPUT.star --output_root_name OUTPUT --newboxsize 128 --batchsize 5000`

Run `python read_star_shift_crop_and_generate_new_star_v3.py -h` for help. The batchsize can be larger if you have many RAM. Otherwise ~ 10000 is recommended.

Outputs will be one OUTPUT.star and many OUTPUT_00??.mrcs . Then you can utilize the OUTPUT.star for reconstruction and refinement. This version only supports RELION 3.1 star format (For using the starfile lib)

# Updated 12.17.2022

Fix a critical bug that the rlnDefocusU/V would be completely wrong.

Download and reinstall this.

https://github.com/homurachan/Block-based-recontruction/blob/master/relion-3.1.2_BBR.zip

# Updated 10.21.2022

Created a page in Wiki:

https://github.com/homurachan/Block-based-recontruction/wiki/How-to-fit-block-into-original-map

describing how to fit map of blocks after refinement into their original position.

# Updated 08.13.2022

Created 2 pages in Wiki:

https://github.com/homurachan/Block-based-recontruction/wiki

https://github.com/homurachan/Block-based-recontruction/wiki/How-to-determine-position-of-block

which describe how to combine blocks into full map and how to determine position of block using UCSF Chimera.

Uploaded a small dataset of reovirus, which can be used for practicing BBR: 

https://1drv.ms/u/s!AghYYiVwSrFmhAxUTa0swcXgWJn0?e=BnW1bJ , information is inside of the compressed files. micrograph_ctf.star and refine.star are also included.

Add feature "--remove_nan" in relion_star_handler, which should be used together with "--discard_on_stats". This options read star files and remove the image item that has infinity or NaN in it. It was inspired by our colleague who suffered from a random blank-micrograph.

Move old readme.md to https://github.com/homurachan/Block-based-recontruction/blob/master/old_version/Readme.old2.md

# Updated 05.12.2022

Uploaded the modified version of RELION 3.1.2. Now you can do the process within RELION GUI and pipelines.

Just download the "relion-3.1.2_BBR.zip" (https://github.com/homurachan/Block-based-recontruction/blob/master/relion-3.1.2_BBR.zip), unzip and install like original version of RELION. It can replace RELION3.1.2 since no function change was made to rest parts of RELION. You will find the "Block-based Recons" option on the GUI. 

![alt text](https://github.com/homurachan/Block-based-recontruction/blob/master/BBR.png?raw=true)

Input particles: Just your particles.

Symmetry of particles: Any symmetry within RELION is supported.

X/Y/Z position of reconstruction: The same Point_X, Point_Y, Point_Z below.

Correct/Inverted handerness: Choose the handerness of sub-particles. If both were "NO", no defocus change will be made (for small particles).

X/Y-size of the micrograph: The image size of the micrograph. Program will drop sub-particles that the center lays outside of the micrograph.

Rounded translation: The OriginX/Y will be set to integer rather than float. Just for debug usage.

Samples of input are shown below.

![alt text](https://github.com/homurachan/Block-based-recontruction/blob/master/BBR_param.png?raw=true)

After finish the job, use the output file as "Refined particles STAR file" on I/O of Particle extraction. Please set re-center refined coordinates to (0,0,0). Then adjust the particle box size to block box size.

Reconstruct the output star file by relion_reconstruct --i OUTPUT.STAR --ctf --sym c1 --subset 1/2 --o half1/half2.mrc . (Optional below) Calculated the FSC curve.
You can run 'relion_star_handler --i OUTPUT.STAR --o out.star --do_invert_BBR_handerness' to invert the handerness of the star. Keep the one with higher FSC.

Just ordinary single particle analysis. Remember always use local refinement (Initial angular sampling <= Local searches from auto-sampling in 3D auto-refine)."

# 简体中文 分块重构
包含了分块重构所需的脚本及合并的小程序,遵循WTFPL verion 2 license, a GPL-campatible free license. 改编版RELION遵循GPL ver2 license。
如果这些代码或分块重构算法对你的研究有帮助，请引用: NATURE COMMUNICATIONS (2018) 9:1552 or DOI: 10.1038/s41467-018-04051-9

# 12.17.2022更新

修正了一个严重bug，当循环时sub-particle的defocusU/V会发生完全错误。

下载并重新安装以下版本。

https://github.com/homurachan/Block-based-recontruction/blob/master/relion-3.1.2_BBR.zip

# 10.21.2022更新创建了一页Wiki:

https://github.com/homurachan/Block-based-recontruction/wiki/How-to-fit-block-into-original-map

描述如何把分块重构好的分块fit进原始位置。因为多数情况下refine好的分块会有一个小旋转。

# 08.13.2022更新

创建了两页Wiki:

https://github.com/homurachan/Block-based-recontruction/wiki

https://github.com/homurachan/Block-based-recontruction/wiki/How-to-determine-position-of-block

分别描述如何把多个重构好的分块合并成一个完整的map；以及如何用Chimera确定每个分块的中心位置。

上传了一个可以用来练习分块重构的reovirus的小数据集: 

https://1drv.ms/u/s!AghYYiVwSrFmhAxUTa0swcXgWJn0?e=BnW1bJ ,包含micrograph_ctf.star和refine.star,其他信息在压缩文件的info里.

在relion-3.1.2_BBR.zip的relion_star_handler里增加了--remove_nan功能，需与--discard_on_stats连用。作用是读取star文件，把含有无穷大的图像的条目去除，不改变图像。

# 05.12.2022更新

更新了修改版的RELION 3.1.2. 现在可以使用修改版RELION在GUI中完成分块重构.

下载"relion-3.1.2_BBR.zip" (https://github.com/homurachan/Block-based-recontruction/blob/master/relion-3.1.2_BBR.zip), 解压后比照原始版RELION安装. 该修改版可以完全替代原始版RELION3.1.2. 打开后可以在主界面看到"Block-based Recons"。

![alt text](https://github.com/homurachan/Block-based-recontruction/blob/master/BBR.png?raw=true)

Input particles: 输入文件.

Symmetry of particles: 任何RELION支持的对称性都可以使用.

X/Y/Z position of reconstruction: 如同下文所述的Point_X, Point_Y, Point_Z.

Correct/Inverted handerness: 选择颗粒手性，如果都选NO，那么sub-particle的defocus不会改变，适用于较小的颗粒。

X/Y-size of the micrograph: micrograph的尺寸，必须是particle extraction里使用的. 程序会把中心落在micrograph外的sub-particle扔掉.

Rounded translation: OriginX/Y变为整数，只在测试时使用（防止插值误差）.

下图是一些参数样本.
![alt text](https://github.com/homurachan/Block-based-recontruction/blob/master/BBR_param.png?raw=true)

生成的star文件放到relion -> Particle extraction -> I/O -> OR re-extract refined particles = yes -> "Refined particles STAR file"这里,同时选中OR: re-center refined coordinates = yes.接下来就重新选择Particle box size为block大小就行了.

判断手性,用'relion_reconstruct --i OUTPUT.STAR --ctf --sym c1 --subset 1/2 --o half1/half2.mrc'重构组合好/生成好的star文件. 如果不想判断手性也行，可忽略下面的测试.用relion_postprocess计算FSC.用'relion_star_handler --i OUTPUT.STAR --o out.star --do_invert_BBR_handerness'来生成相反手性的star,重构后比较FSC.保留FSC较高的那个.对于C/D对称的样品,建议前面的手性部分选"2",即不改变block defocus.因为一般来说C/D对称的解不到接近Ewald Sphere极限的分辨率.

正常的单颗粒分析流程,最好总是进行局域refine (Initial angular sampling <= Local searches from auto-sampling in 3D auto-refine)

移动老版本的readme.md到https://github.com/homurachan/Block-based-recontruction/blob/master/old_version/Readme.old2.md

# 额外功能

在relion_star_handler里更新了--do_rotation功能，使用如下命令："relion_star_handler --i input.star --o output.star --do_rotation --rOt rotangle --tIlt tiltangle --pSi psiangle". 该命令能把input.star所对应的重构按照RELION使用的ZYZ欧拉角体系旋转rotangle-tiltangle-psiangle，适用于relion_align_symmetry的输出结果. 这样就不需要重新跑class3D.
