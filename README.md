# Block-based-recontruction
Scripts and sources of the block-based reconstruction/refinement
These scripts and codes are under WTFPL verion 2 license, a GPL-campatible free license.
Please cite our paper: NATURE COMMUNICATIONS (2018) 9:1552 or DOI: 10.1038/s41467-018-04051-9
if our block-based reconstruction idea or these codes work.

# Updated 06.28.2020

The scripts only work with relion ver3.0 or earlier star files. A "for_straightforward_relion_v2/relion31_star_to_30_v2.py" script can be used to convert refined relion 3.1 particle star to 3.0ver.

As everyone prefers relion rather than JSPR, I uploaded a modified relion 3.0.8 version to perform block refinement under the folder for_straightforward_relion_v2. Just download the relion-3.0.8_modi_able_to_write_subparticle.zip, decompress and compile just the same as relion does. It works like original relion v3.0.8 other than relion_preprocess, I also add 2 metadata lable "rlnDeltaZ" and "rlnParticleSerialNumber". Remember to remove these columns if you wish to use the star file on original relion.
	
1.	If you only have the particle images, use "for_straightforward_relion_v2/BBR_with_relion_v8.py"
The usage is 'python ./BBR_with_relion_v8.py INPUT.STAR Point_X Point_Y Point_Z PARTICLE_BOXSIZE OUTPUT.STAR HANDERNESS_OPTION MICROGRAPH_SIZE_X MICROGRAPH_SIZE_Y SYM'

A=(Point_X, Point_Y, Point_Z) is a 3D coordinate of the reconstructed map. the origin of A is (PARTICLE_BOXSIZE/2, PARTICLE_BOXSIZE/2, PARTICLE_BOXSIZE/2) . MICROGRAPH_SIZE_X/Y are needed to drop subparticles lay outside of the micrograph (Most of them would be 0-value and unusable). Current supported symmetry is C-n / D-n and I3 symmetry.

PS. One of the very easy way to find a certain point of the map is to use UCSF Chimera's volume eraser. Firstly erasing the wanted point with a large enough sphere, saving the map, then using 'v2 yoursave.mrc' command of EMAN package, middle clicking the map, finding coordinates of the center of the erased sphere. Those can be used for my script directly.

Then use 'python ./split_star_for_preprocessing.py OUTPUT.STAR PATCH_NUM ROOT_NAME BLOCK_SIZE RUNORT_FILE_NAME' to split the OUTPUT.STAR. Because particle operation of relion_preprocess cannot be run by relion_preprocess_mpi, we have to split the star file to run the preprocessing parallelly. 
Run the suggested command of split_star_for_preprocessing.py to combine the processed stack star files.

The runort file can be run by runpar of EMAN, or other program.

2.	If you have the micrograph, use "for_straightforward_relion_v2/BBR_with_relion_v8.py" and use the output result as "Refined particles STAR file" on I/O of Particle extraction. Please set re-center refined coordinates to (0,0,0). Then adjust the particle box size to block box size, and it's done.

3.	Reconstruct the combined star file by relion_reconstruct --i COMBINED.STAR --ctf --sym c1 --subset 1/2 --o half1/half2.mrc . Calculated the FSC curve.
You can run 'read_block_based_debug_delta_z_invert_handerness.py' to test the handerness of the reconstruced maps. Keep the one with higher FSC.

4.	Just ordinary single particle analysis.

# 简体中文 分块重构
包含了分块重构所需的脚本及合并的小程序,遵循WTFPL verion 2 license, a GPL-campatible free license.
如果这些代码或分块重构算法对你的研究有帮助，请引用: NATURE COMMUNICATIONS (2018) 9:1552 or DOI: 10.1038/s41467-018-04051-9

# 06.28.2020更新

以下脚本仅适用于relion3.0版本或更低版本.若使用relion3.1,可用"for_straightforward_relion_v2/relion31_star_to_30_v2.py"脚本将relion3.1的star转换成relion3.0版本。

既然大家都更喜欢relion,我在for_straightforward_relion_v2文件夹下上传了一个改编版的relion 3.0.8 .安装方法和relion3完全相同,也完全兼容,仅增加了一个relion_preprocess中的选项,我同时也增加了两个metadata标签"rlnDeltaZ"和"rlnParticleSerialNumber".正常的relion不读这两个标签,可以用relion_star_handler --remove_column把它们去掉.这两个标签其实很有用,所以我建议替换掉原始的relion3.0.8 .
	
1.	如果仅有particle文件,使用"for_straightforward_relion_v2/BBR_with_relion_v8.py"
使用方法'python ./BBR_with_relion_v8.py INPUT.STAR 点X 点Y 点Z PARTICLE_BOXSIZE OUTPUT.STAR 手性选择 MICROGRAPH_SIZE_X MICROGRAPH_SIZE_Y 对称性'

A=(点X, 点Y, 点Z) 是属于3D重构的坐标. 点A的原点是(PARTICLE_BOXSIZE/2, PARTICLE_BOXSIZE/2, PARTICLE_BOXSIZE/2) . MICROGRAPH_SIZE_X/Y用来丢弃跑到micrograph外面的块,在只有半个病毒的时候比较有用. 目前支持C-n / D-n 和I3对称,未来可能增加I1对称,因为绝大多数人偏好用I1,但其实对结果无任何影响.

注: 一种简单的找点方法是使用UCSF Chimera的volume eraser. 首先擦除掉想要的点,保存,可以使用EMAN的'v2 yoursave.mrc',中键点击打开的图,看被擦除的坐标.这些坐标能被我的脚本直接使用.

接下来使用'python ./split_star_for_preprocessing.py OUTPUT.STAR 每组分多少张子图 ROOT_NAME 分块大小 批处理命令'来分割OUTPUT.STAR.因为relion_preprocess的particle processing不能使用多线程的relion_preprocess_mpi,我们必须手动分割,手动跑多线程. 运行split_star_for_preprocessing.py给出的建议命令来整合跑完以后的star文件.跑多线程可以用EMAN的runpar或其他的程序,如张凯(Yale U)编写的脚本.

2.	如果你有micrograph,非常简单,使用"for_straightforward_relion_v2/BBR_with_relion_v8.py"把生成的star文件放到relion -> Particle extraction -> I/O -> OR re-extract refined particles = yes -> "Refined particles STAR file"这里,同时选中OR: re-center refined coordinates = yes.接下来就重新选择Particle box size为block大小就行了.

3.	Reconstruct the combined star file by relion_reconstruct --i COMBINED.STAR --ctf --sym c1 --subset 1/2 --o half1/half2.mrc . Calculated the FSC curve.
You can run 'read_block_based_debug_delta_z_invert_handerness.py' to test the handerness of the reconstruced maps. Keep the one with higher FSC.

4.	Just ordinary single particle analysis.

# OLD
	To compile the C codes, you should have installed EMAN 1.9. Also check your g++ version, 4.8 and 5.x works fine to me, but 6.3 occurs errors.
	For example, use "g++ addup_many_part_into_full_icos.c -o addup_many_part_into_full_icos -IwhereyouinstallEMAN/include whereyouinstallEMAN/lib/libEM.so" to complie.

	0. Make sure the symmetry used in relion is I3 for icosahedral symmetry, or my script cannot convert the euler angles to EMAN's icos symmetry.

	Workflow:

	1. You need a full-size model (can be from relion) and particles set in EMAN or EMAN2 list form by executing "./relion2lst.py refined_starfile.star --lst anyname.lst" . Make sure to use the relion2lst.py in this folder.
	
	2. If the symmetry is icos, convert the "anyname.lst" to correct EMAN list by doing: "./change_I3_sym_to_EMAN_angle.py anyname.lst anyname2.lst". If the symmetry is not icosahedral, do not do this step.
	
	3. Split the EMAN list file to even/odd cession by doing "./relion2lst_even_odd.py refined_starfile.star m+4 anyname2.lst odd_name.lst even_name.lst". To determine m, head the star file, the FINAL line of metadata is something like "_rlnRandomSubset #29" or "_rlnNrOfSignificantSamples #24" , m=29 or m=24.

	4. Find certain points in the model (x0,y0,z0), assuming the origin of coordinates is (nx/2,ny/2,nz/2). e.g., for a 300*300*300 map, the center of map is (150,150,150)

	5. Use df_change_for_symmetric_unit_debug1.py (for icosahedral symmetry), or df_change_for_symmetric_unit_debug1_for_Cx-sym.py (for Cn Symmetry), or df_change_for_symmetric_unit_debug1_for_Dx-sym.py (for Dn symmetry) to generate output list, if you use icoshedral symmetry, the output should contain 59 times lines more than the original list. the debug option is set to determine the handedness. Use both 0,1 to produce list, and do reconstruction of the lists. Compare the FSC between the Odd/Even part of the data. The higher FSC value means the current handedness. e.g. debug_0 is higher and the handedness is reversed.
	e.g. "./df_change_for_symmetric_unit_debug1_for_Cx-sym.py anyname.lst x0 y0 z0 pixel_size full_map_size_ny n_for_Cn_sym anyoutput.lst 1"

	6. Use split_lst.py to split the output in order to to multi-task procession. If particle number is not large, or in a pbs server, this step can be skipped, but it will cost more time.

	7. Try proc3d relion_refine_result.mrc small_block.mrc clip=a,a,a,x0,y0,z0	, and judge wheter the "a" value is suitable. When a is too small, the map will not cover all the needed area.

	8. Use e2proc2d.py from JSPR package, doing centralizing and clipping by executing "e2proc2d.py input.lst output.spi --process=xform.centerbyxform --clip=a,a", where a is the ny size of the small blocks and input.lst is the output of step3.

	9. Execute "./remove_misc_in_lst-center.py input.lst output.spi output.lst a/2 cs voltage 1" to convert input.lst to a list file (output.lst) corresponded to output.spi

	10. Convert the output.lst to relion star file by executing "./jspr_refine_2_relion_nofilename.py output.lst a pixel_size voltage cs odd/even Outout.star" if step4 is skipped. Or use ./jspr_refine_2_relion.py instead.

	11. Executing "cat ./to_add_star_metadata.txt Output.star >> real_full_output.star", to generate a real relion star file. Now a relion refinement can be performed. But make sure in Auto-sampling card, 'Initial angular sampling' is equal to 'Local searches from auto-sampling'. A good value is 1.8 degree for both.
	
  I found cisTEM works very well with local refinement, but don't do over refine, 2 cycles are often enough.
  
	More information can be found in each file.

#	09.03.2019 added:

	In for_straight_forward_relion folder you can find scripts to write a star file bypassing EMAN2 or JSPR processing.
	
	You HAVE TO USE "I3" symmetry in relion. The model from relion_reconstruct should be processed by
	'proc3d model.mrc model_rot.mrc rot=0,180,0' to get a map corresponding to EMAN's icosahedral system.
	
	1. From a original star file, excuting "./relion2lst_nooutput.py a.star --lst ANYNAME.lst --allrelion 1 --ny RELION_BOXSIZE".
	This script requires EMAN2 being installed.
	
	2. Executing "./change_I3_sym_to_EMAN_angle_v3.py ANYNAME.lst ANYNAME_2.lst" to change from I3 sym to EMAN system.
	
	3. Just like step 5 above.
	
	4. Executing "./jspr_refine_2_relion_nofilename_for_relion.py output_by_step3.lst RELION_BOXSIZE tmp.star"
	
	5. 'cat ./to_add_star_metadata_v2.txt tmp.star >> final.star'
	
	6. './check_sub_particle_position.py final.star 30 CAMERA_NX CAMERA_NY final_check.star' In case some sub-particles lie
	outside of the micrograph and induce "...particle lies completely outside of micrograph" error in relion.
	
	The "final_check.star" can be used in relion 2 or 3 as "Refined particles STAR file" at "Particle extraction".
	The rest is conventional way to do SPA.
#	11.08.2019 added:

	If the particle has Cn or Dn symmetry, use df_change_for_symmetric_unit_debug1_for_relion_Cn_Dn.py.
	
	1. From a original star file, excuting "./relion2lst_nooutput.py a.star --lst ANYNAME.lst --allrelion 1 --ny RELION_BOXSIZE".
	This script requires EMAN2 being installed.
	
	2. e.g. A C3 protein should run this: "df_change_for_symmetric_unit_debug1_for_relion_Cn_Dn.py ANYNAME.lst X Y Z pixel_size box_size ANYNAME_2.lst C 3 2".
	For small proteins, I suggest not to use block defoci for blocks.
	
	3. The same as step 3/4/5/6 above.
