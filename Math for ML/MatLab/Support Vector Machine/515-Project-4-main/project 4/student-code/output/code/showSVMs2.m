function  showSVMs2(w,b,eta,ll,mm,nw)
%  
%  Function to display the result of running SVM
%  on p blue points u_1, ..., u_p in u 
%  and q red points v_1, ..., v_q in v

l = makeline(w,b,ll,mm,nw);        %  makes separating line
lm1 = makeline(w,b+eta,ll,mm,nw);  %  makes blue margin line
lm2 = makeline(w,b-eta,ll,mm,nw);  %  makes red margin line

plot(l(1,:),l(2,:),'-m','LineWidth',1.2)            %  plots separating line
plot(lm1(1,:),lm1(2,:),'-b','LineWidth',1.2)        %  plots blue margin line
plot(lm2(1,:),lm2(2,:),'-r','LineWidth',1.2)        %  plots red margin line
hold off
end

