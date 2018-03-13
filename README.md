# Block-based-recontruction
Scripts and sources of the block-based reconstruction/refinement
These script and codes are under Do What The Fuck You Want To Public License (or maybe GPL-3.0 as required by the editor).
Please cite our paper if our block-based reconstruction idea or these shitty codes work.

	To compile the C codes, you should have installed EMAN 1.9. Also check your g++ version, 4.8 and 5.x works fine to me, but 6.3 occurs errors.
	For example, use "g++ addup_many_part_into_full_icos.c -o addup_many_part_into_full_icos -IwhereyouinstallEMAN/include whereyouinstallEMAN/lib/libEM.so" to complie.
	To do local refine (or focus refine as mentioned by Wen Jiang), it's more convenient to use JSPR or cisTEM package.
	
	Workflow:
	1. You need a full-size model and particles set in EMAN or EMAN2 list form.
	2. Find certain points in the model, assuming the origin of coordinates is (ny/2,ny/2,ny/2).
	3. Use df_change_for_symmetric_unit_debug1.py to generate output list, if you use icoshedral symmetry, the output should contain 59 times lines more than the original list. the debug option is set to determine the handedness.Use both 0,1 to produce list, and do reconstruction of the lists. Compare the FSC between the Odd/Even part of the data. The higher FSC value means the current handedness. e.g. debug_0 is higher and the handedness is reversed.
	4. Use split_lst.py to split the output in order to to multi-task procession.
	5. Use e2proc2d.py in JSPR package, performing centralizing and clipping by executing "e2proc2d.py input.lst output.hdf --process=xform.centerbyxform --clip=a,a", where a is the ny size of the small blocks.
	6. Use remove_misc_in_lst-center.py to change the "center" of previous output list.
	7. Perform local refinement.
	8. After reconstruction of each block, use addup_many_part or addup_many_part_into_full_icos to make a full model, or you can skip this if just evaluating.
	
  I found cisTEM works very well with local refinement, but don't do over refine, 2 cycles are often enough.
  
	More information can be found in each file.
