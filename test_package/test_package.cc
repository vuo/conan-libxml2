#include <stdio.h>
#include <libxml/parser.h>

int main()
{
	xmlInitParser();
	printf("Successfully initialized libxml2.\n");
	return 0;
}
