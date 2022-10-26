with open('tranco.txt','r') as rf:
  with open('arranged_tranco.txt','w') as wf:
    for line in rf:
      wf.write(line[line.index(',')+1:])