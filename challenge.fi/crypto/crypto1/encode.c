#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>



int main(int argc, char **args)
{
    FILE *fin;
    FILE *fout;
    uint32_t fs;
    uint32_t fptr;
    uint8_t dbuf[2];
    uint8_t rbcnt;
    uint8_t tmp;
    uint32_t mask;

    if (argc != 3) {
        printf("\nUsage: ./encode [input_f] [output_f]\n\n");
        printf("[input_f] : File which contents are to be encrypted\n");
        printf("[output_f] : File where encrypted contents are stored\n\n");
        return 1;
    }

    fin = fopen(args[1], "rb");
    if (!fin) {
        printf("Error! Input file could not be opened!\n");
        return 1;
    }

    fout = fopen(args[2], "wb");
    if (!fout) {
        printf("Error! Could not create output file!\n");
        fclose(fin);
        return 1;
    }

    fseek(fin, 0, SEEK_END);
    fs = ftell(fin);
    if (!fs) {
        printf("Error! Input file is empty!\n");
        fclose(fin);
        fclose(fout);
        return 1;
    }

    // Evil magic trix
    mask = (0xa5a5a5a5) ^ (0x5a5a5a5a);
    mask &= (mask >> 24);

    fseek(fin, 0, SEEK_SET);
    if (fs <= 2) {
        fread(dbuf, sizeof(uint8_t), fs, fin);
        if ((fs % 2) == 0) {
            tmp = (dbuf[0] ^ 0xa5) & mask;
            dbuf[0] = ~(dbuf[1] & mask);
            dbuf[1] = ~tmp;
            fwrite(dbuf, sizeof(uint8_t), fs, fout);
        }
        else {
            dbuf[0] = ~(dbuf[0] & mask);
        }
    }
    else {
        rbcnt = 2;
        for (fptr = 0; fptr < fs; fptr = fptr + 2) {
            if (rbcnt > (fs - fptr)) {
                rbcnt = fs - fptr;
            }
            fread(dbuf, sizeof(uint8_t), rbcnt, fin);
            if ((rbcnt % 2) == 0) {
                tmp = (dbuf[0] ^ 0xa5) & mask;
                dbuf[0] = ~(dbuf[1] & mask);
                dbuf[1] = ~tmp;
                fwrite(dbuf, sizeof(uint8_t), rbcnt, fout);
            }
            else {
                dbuf[0] = ~(dbuf[0] & mask);
                fwrite(dbuf, sizeof(uint8_t), rbcnt, fout);
            }
        }
    }
    fclose(fin);
    fclose(fout);
    return 0;
}
