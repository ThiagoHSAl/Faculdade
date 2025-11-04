{
  printf("%s %s %s %s",$1,$2,$4,$3)
  for (i=5;i<=NF;i++){
    printf(" %s",$i)
  }
  printf("\n");
}

