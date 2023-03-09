run subdecas

  bx1=[0 1 2 3;];
  by1=[0 4 5 0];
n=2;
[ud,ld] = subdecas(bx1,by1,n);
plot(ud(1,:),ud(2,:))