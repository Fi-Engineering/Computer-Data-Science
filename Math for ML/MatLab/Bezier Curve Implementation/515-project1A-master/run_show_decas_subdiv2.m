  bx=[4 0 6 2];
  by=[0 6 6 0];
    
n=6;
[xx,yy]=show_decas_subdiv2(transpose(bx),transpose(by),n);

figure;
hold on
plot(bx,by,'g-')
plot(xx,yy,'b-')
hold off