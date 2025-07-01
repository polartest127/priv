#include <stdio.h>

int main() {







FILE *fptr;

fptr = fopen("LummaTextResources.txt", "w");

fprintf(fptr, "LummyLummaYummyYumma");

fclose(fptr);
}