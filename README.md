# Block-based-recontruction
Scripts and sources of the block-based reconstruction/refinement
These scripts and codes are under WTFPL verion 2 license, a GPL-campatible free license.
Please cite our paper: NATURE COMMUNICATIONS (2018) 9:1552 or DOI: 10.1038/s41467-018-04051-9
if our block-based reconstruction idea or these codes work.
# Updated 08.18.2020

Added Octane symmetry support at for_straightforward_relion_v2/BBR_with_relion_v9.py .

# Updated 06.28.2020

The scripts only work with relion ver3.0 or earlier star files. A "for_straightforward_relion_v2/relion31_star_to_30_v2.py" script can be used to convert refined relion 3.1 particle star to 3.0ver.

As everyone prefers relion rather than JSPR, I uploaded a modified relion 3.0.8 version to perform block refinement under the folder for_straightforward_relion_v2. Just download the relion-3.0.8_modi_able_to_write_subparticle.zip, decompress and compile just the same as relion does. It works like original relion v3.0.8 other than relion_preprocess, I also add 2 metadata lable "rlnDeltaZ" and "rlnParticleSerialNumber". Remember to remove these columns if you wish to use the star file on original relion.
	
1.	If you only have the particle images, use "for_straightforward_relion_v2/BBR_with_relion_v8.py"
The usage is 'python ./BBR_with_relion_v8.py INPUT.STAR Point_X Point_Y Point_Z PARTICLE_BOXSIZE OUTPUT.STAR HANDERNESS_OPTION MICROGRAPH_SIZE_X MICROGRAPH_SIZE_Y SYM'

A=(Point_X, Point_Y, Point_Z) is a 3D coordinate of the reconstructed map. The map should follow EMAN coordinates. The EMAN coordinates are the same as relion's spider coordiantes other than I3-sym. You have to use EMAN's 'proc3d map.mrc output.mrc rot=0,180,0' to convert I3-map to EMAN's icosahedral map, then to find A=(X,Y,Z). The origin of A is (PARTICLE_BOXSIZE/2, PARTICLE_BOXSIZE/2, PARTICLE_BOXSIZE/2) . MICROGRAPH_SIZE_X/Y are needed to drop subparticles lay outside of the micrograph (Most of them would be 0-value and unusable). Current supported symmetry is C-n / D-n and I3 symmetry.

PS. One of the very easy way to find a certain point of the map is to use UCSF Chimera's volume eraser. Firstly erasing the wanted point with a large enough sphere, saving the map, then using 'v2 yoursave.mrc' command of EMAN package, middle clicking the map, finding coordinates of the center of the erased sphere. Those can be used for my script directly.

Then use 'python ./split_star_for_preprocessing.py OUTPUT.STAR PATCH_NUM ROOT_NAME BLOCK_SIZE RUNORT_FILE_NAME' to split the OUTPUT.STAR. Because particle operation of relion_preprocess cannot be run by relion_preprocess_mpi, we have to split the star file to run the preprocessing parallelly. 
Run the suggested command of split_star_for_preprocessing.py to combine the processed stack star files.

The runort file can be run by runpar of EMAN, or other program.

2.	If you have the micrograph, use "for_straightforward_relion_v2/BBR_with_relion_v8.py" and use the output result as "Refined particles STAR file" on I/O of Particle extraction. Please set re-center refined coordinates to (0,0,0). Then adjust the particle box size to block box size, and it's done.

3.	Reconstruct the combined star file by relion_reconstruct --i COMBINED.STAR --ctf --sym c1 --subset 1/2 --o half1/half2.mrc . Calculated the FSC curve.
You can run 'read_block_based_debug_delta_z_invert_handerness.py' to test the handerness of the reconstruced maps. Keep the one with higher FSC.

4.	Just ordinary single particle analysis. Remember always use local refinement (Initial angular sampling <= Local searches from auto-sampling in 3D auto-refine).

Old readme.md moved to readme.old

# 简体中文 分块重构
包含了分块重构所需的脚本及合并的小程序,遵循WTFPL verion 2 license, a GPL-campatible free license.
如果这些代码或分块重构算法对你的研究有帮助，请引用: NATURE COMMUNICATIONS (2018) 9:1552 or DOI: 10.1038/s41467-018-04051-9

# 08.18.2020更新

在for_straightforward_relion_v2/BBR_with_relion_v9.py中增加了对Octane对称性的支持。

# 06.28.2020更新

以下脚本仅适用于relion3.0版本或更低版本.若使用relion3.1,可用"for_straightforward_relion_v2/relion31_star_to_30_v2.py"脚本将relion3.1的star转换成relion3.0版本。

既然大家都更喜欢relion,我在for_straightforward_relion_v2文件夹下上传了一个改编版的relion 3.0.8 .安装方法和relion3完全相同,也完全兼容,仅增加了一个relion_preprocess中的选项,我同时也增加了两个metadata标签"rlnDeltaZ"和"rlnParticleSerialNumber".正常的relion不读这两个标签,可以用relion_star_handler --remove_column把它们去掉.这两个标签其实很有用,所以我建议替换掉原始的relion3.0.8 .
	
1.	如果仅有particle文件,使用"for_straightforward_relion_v2/BBR_with_relion_v8.py"
使用方法'python ./BBR_with_relion_v8.py INPUT.STAR 点X 点Y 点Z PARTICLE_BOXSIZE OUTPUT.STAR 手性选择 MICROGRAPH_SIZE_X MICROGRAPH_SIZE_Y 对称性'

A=(点X, 点Y, 点Z) 是属于3D重构的坐标. 点A的原点是(PARTICLE_BOXSIZE/2, PARTICLE_BOXSIZE/2, PARTICLE_BOXSIZE/2) . MICROGRAPH_SIZE_X/Y用来丢弃跑到micrograph外面的块,在只有半个病毒的时候比较有用. 目前支持C-n / D-n 和I3对称,未来可能增加I1对称,因为绝大多数人偏好用I1,但其实对结果无任何影响.点A必须遵守EMAN坐标,对于C/D对称,EMAN坐标与relion的spider坐标相同.对于I3对称,在找点前必须用EMAN的proc3d进行'proc3d relion.mrc output.mrc rot=0,180,0'将图转换至EMAN的icosahedral坐标,才能用v2找点.

注: 一种简单的找点方法是使用UCSF Chimera的volume eraser. 首先擦除掉想要的点,保存,可以使用EMAN的'v2 yoursave.mrc',中键点击打开的图,看被擦除的坐标.这些坐标能被我的脚本直接使用.

接下来使用'python ./split_star_for_preprocessing.py OUTPUT.STAR 每组分多少张子图 ROOT_NAME 分块大小 批处理命令'来分割OUTPUT.STAR.因为relion_preprocess的particle processing不能使用多线程的relion_preprocess_mpi,我们必须手动分割,手动跑多线程. 运行split_star_for_preprocessing.py给出的建议命令来整合跑完以后的star文件.跑多线程可以用EMAN的runpar或其他的程序,如张凯(Yale U)编写的脚本.

2.	如果你有micrograph,非常简单,使用"for_straightforward_relion_v2/BBR_with_relion_v8.py"把生成的star文件放到relion -> Particle extraction -> I/O -> OR re-extract refined particles = yes -> "Refined particles STAR file"这里,同时选中OR: re-center refined coordinates = yes.接下来就重新选择Particle box size为block大小就行了.

3.	判断手性,用'relion_reconstruct --i COMBINED.STAR --ctf --sym c1 --subset 1/2 --o half1/half2.mrc'重构组合好/生成好的star文件.用relion_postprocess计算FSC.用'read_block_based_debug_delta_z_invert_handerness.py input.star invert.star'来生成相反手性的star,重构后比较FSC.保留FSC较高的那个.对于C/D对称的样品,建议前面的手性部分选"2",即不改变block defocus.因为一般来说C/D对称的解不到接近Ewald Sphere极限的分辨率.

4.	正常的单颗粒分析流程,最好总是进行局域refine (Initial angular sampling <= Local searches from auto-sampling in 3D auto-refine)

