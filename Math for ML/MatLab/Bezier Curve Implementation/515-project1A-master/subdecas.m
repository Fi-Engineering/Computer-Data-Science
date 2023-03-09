
% subdecas that takes as input a control polygon
% cpoly (a 2 x 4 matrix) and returns the two control polygons ud and ld produced after one
% step of the de Casteljau subdivision algorithm.

function [ud,ld] = subdecas(bx1,by1,n)
    [x,y] = decas_subdiv2(bx1,by1,n);
    n1=size(x,2);
    n3=int32(n1)/2;
    udx=x(1:n3);
    udy=y(1:n3);
    ud=[udx;udy];
    ulx=x(n3:n1);
    uly=y(n3:n1);
    ld=[ulx;uly];
end

