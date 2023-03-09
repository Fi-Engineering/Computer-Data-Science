%makes the vectors x and y described earlier from 1poly

function [x,y] = makelist(cpoly,n)
    [r,l] = size(cpoly);
    x=[];
    y=[];

    for i=1:l
        A= cpoly{1,i};
        bx1=A(1,:);
        by1=A(2,:);
        [x1,y1] = decas_subdiv2(bx1,by1,n);
        x=[x,x1];
        y= [y,y1];
    end
    xt = transpose(x);
    yt=transpose(y);
    xyt=[xt,yt];
    xy=unique(xyt,'row');
    x=xy(:,1);
    y=xy(:,2);
    x=transpose(x);
    y=transpose(y);
end