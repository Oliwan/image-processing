#include <stdio.h>
#include <jpeglib.h>
#include <iostream>

using namespace std;

JBLOCKARRAY rowPtrs[MAX_COMPONENTS];

void read(jpeg_decompress_struct srcinfo, jvirt_barray_ptr * src_coef_arrays) {
  //TODO: select the channel to be extracted, now extracting (bulk) all the three
  for (JDIMENSION compNum=0; compNum < srcinfo.num_components; compNum++) {
    for (JDIMENSION rowNum=0; rowNum < srcinfo.comp_info[compNum].height_in_blocks; rowNum++) {
      // Loop through each row
        for(JDIMENSION j=0; j<8; j++){
          // A pointer to the virtual array of dct values
          rowPtrs[compNum] = ((&srcinfo)->mem->access_virt_barray)((j_common_ptr) &srcinfo, src_coef_arrays[compNum],rowNum, (JDIMENSION) 1, FALSE);
          // Loop through the blocks to get the dct values
          for (JDIMENSION blockNum=0; blockNum < srcinfo.comp_info[compNum].width_in_blocks; blockNum++){
            //...iterate over DCT coefficients
            for (JDIMENSION i=j*8; i<j*8+8; i++){
              //and print them to standard out - one per line
              cout << rowPtrs[compNum][0][blockNum][i] << endl;
          }
        }
      }
    }
  }
}

int main(int argc, char *argv[]) {
  const char* filename = argv[1];
  
  FILE * infile;  
  struct jpeg_decompress_struct srcinfo;
  struct jpeg_error_mgr srcerr;

  if ((infile = fopen(filename, "rb")) == NULL) {
    fprintf(stderr, "can't open %s\n", filename);
    return 0;
  }

  srcinfo.err = jpeg_std_error(&srcerr);
  jpeg_create_decompress(&srcinfo);
  jpeg_stdio_src(&srcinfo, infile);
  (void) jpeg_read_header(&srcinfo, FALSE);
  
  //coefficients
  jvirt_barray_ptr * src_coef_arrays = jpeg_read_coefficients(&srcinfo);
  read(srcinfo, src_coef_arrays);
    
  jpeg_destroy_decompress(&srcinfo);
  fclose(infile);
  return 0; 
}
