import starfile
import mrcfile
import numpy as np
import os,argparse

def translation_twoD_image(image,trans_X,trans_Y):
	# transX/Y are all in pixels. Ingore the decimal part.
	# image should be cp array and in real space.
	# crop the density outside after trans.
	trans_x=int(np.floor(trans_X+0.5))
	trans_y=int(np.floor(trans_Y+0.5))
	ysize, xsize = image.shape

	# Determine the start and end indices for slicing
	start_x = max(0, trans_x)
	end_x = xsize if trans_x >= 0 else xsize + trans_x
	start_y = max(0, trans_y)
	end_y = ysize if trans_y >= 0 else ysize + trans_y

	# Initialize the translated image with zeros
	translated_image = np.zeros_like(image)

	# Fill the translated image with the appropriate slice of the original image
	translated_image[start_y:end_y, start_x:end_x] = image[max(0, -trans_y):ysize - max(0, trans_y), max(0, -trans_x):xsize - max(0, trans_x)]

	return translated_image
def create_gridsearch_parser():
	parser = argparse.ArgumentParser(description="Crop block images from particle images. The star file should be the output of relion-BBR or relion-SIRM")
	parser.add_argument("--star_name", type=str, required=True, help="Input star file")
	parser.add_argument("--output_root_name", type=str, default="output", help="Output root name of star and stack files. Default = output. So every stack has name of output_000x.mrcs. And the output star has name output.star")
	parser.add_argument("--newboxsize", type=int, default=128, help="The block boxsize in pixel. Default = 128")
	parser.add_argument("--batchsize", type=int, default=5000, help="Number of sub-particles in one stack. Default = 5000. Split the output stacks in order to prevent from using too much RAM.")
	return parser
if __name__ == "__main__":
	parser = create_gridsearch_parser()
	args = parser.parse_args()
	star_name = args.star_name
	output_root_name = args.output_root_name+"_"
	crop_size = args.newboxsize
	batch_size = args.batchsize
	# Load the .star file
	star_data = starfile.read(star_name)
	
	# Extract relevant columns
	origin_x_angst = star_data["particles"]["rlnOriginXAngst"].to_numpy()
	origin_y_angst = star_data["particles"]["rlnOriginYAngst"].to_numpy()
	image_names = star_data["particles"]["rlnImageName"].to_numpy()
	pixel_size = star_data["optics"]["rlnImagePixelSize"].iloc[0]  # Assuming same pixel size for all images

	# Convert shifts from Ångström to integer pixels
	origin_x_pixels = (origin_x_angst / pixel_size)
	origin_y_pixels = (origin_y_angst / pixel_size)
	
	num_batches = (len(image_names) + batch_size - 1) // batch_size  # Compute total batches

	# Prepare new STAR file data
	new_image_names = []
	batch_index = 1
	batch_images = []
	h = -1
	w = -1
	for i, image_name in enumerate(image_names):
		# Extract the MRC file name and particle index
		index, mrc_filename = image_name.split('@')
		index = int(index) - 1  # RELION indices start from 1

		# Open the corresponding MRC file
		with mrcfile.mmap(mrc_filename, mode='r') as mrc:
			image = mrc.data[index]

		# Get image dimensions
		if(h<0 and w < 0):
			h, w = image.shape
		shifted_image = np.zeros_like(image)

		# Compute valid region after shifting
		shift_x, shift_y = origin_x_pixels[i], origin_y_pixels[i]

		shifted_image = translation_twoD_image(image,shift_x,shift_y)

		# Crop the image
		center_x, center_y = w // 2, h // 2
		cropped_image = shifted_image[
			center_y - crop_size // 2 : center_y + crop_size // 2,
			center_x - crop_size // 2 : center_x + crop_size // 2,
		]

		batch_images.append(cropped_image)
		new_mrc_filename = f"{output_root_name}{batch_index:04d}.mrcs"
		new_image_names.append(f"{len(batch_images)}@{new_mrc_filename}")

		# Save when batch reaches batch_size or last image
		if len(batch_images) == batch_size or i == len(image_names) - 1:
			cropped_stack = np.array(batch_images, dtype=np.float32)

			with mrcfile.new(new_mrc_filename, overwrite=True) as new_mrc:
				new_mrc.set_data(cropped_stack)

			print(f"Saved {new_mrc_filename} with {len(batch_images)} images.")

			batch_images = []  # Reset batch list
			batch_index += 1  # Increment batch index

	# Create a new .star file with updated entries
	new_star_data = star_data.copy()
	new_star_data["particles"]["rlnImageName"] = new_image_names
	new_star_data["particles"]["rlnOriginXAngst"] = 0.0
	new_star_data["particles"]["rlnOriginYAngst"] = 0.0
	new_star_data["optics"]["rlnImageSize"] = crop_size

	# Save the new .star file
	starfile.write(new_star_data, args.output_root_name+".star", overwrite=True)

	print("New STAR file saved as ",args.output_root_name+".star")
