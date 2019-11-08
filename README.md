# Block-based-recontruction
Scripts and sources of the block-based reconstruction/refinement
These scripts and codes are under WTFPL verion 2 license, a GPL-campatible free license.
Please cite our paper: NATURE COMMUNICATIONS (2018) 9:1552 or DOI: 10.1038/s41467-018-04051-9
if our block-based reconstruction idea or these codes work.

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
	
	4. Executing "./jspr_refine_2_relion_nofilename_for_relion.py ANYNAME_2.lst RELION_BOXSIZE tmp.star"
	
	5. 'cat ./to_add_star_metadata_v2.txt tmp.star >> final.star'
	
	6. './check_sub_particle_position.py final.star 30 CAMERA_NX CAMERA_NY final_check.star' In case some sub-particles lie
	outside of the micrograph and induce "...particle lies completely outside of micrograph" error in relion.
	
	The "final_check.star" can be used in relion 2 or 3 as "Refined particles STAR file" at "Particle extraction".
	The rest is conventional way to do SPA.
#	11.08.2019 added:

	If the particle has Cn or Dn symmetry, use df_change_for_symmetric_unit_debug1_for_relion_Cn_Dn.py.
	
	1. From a original star file, excuting "./relion2lst_nooutput.py a.star --lst ANYNAME.lst --allrelion 1 --ny RELION_BOXSIZE".
	This script requires EMAN2 being installed.
	
	2. e.g. A C3 protein should run this: "df_change_for_symmetric_unit_debug1_for_relion_Cn_Dn.py ANYNAME.lst X Y Z pixel_size box_size ANYNAME_2.lst C 3 2". For small proteins, I suggest not to use block defoci for blocks.
	
	3. The same as step 3/4/5/6 above.
