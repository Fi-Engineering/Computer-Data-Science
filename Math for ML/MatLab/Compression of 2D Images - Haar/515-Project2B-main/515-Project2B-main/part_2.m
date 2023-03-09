clear X map
load('earth','X')
earth = X(1:256,:);
earth(:,256:256) = 50;
figure
colormap(winter)
imagesc(earth)
encrypt = haar2D(earth);
imagesc(encrypt);

%decode = haar_inv2D(encrypt);
%imagesc(decode);

 

 ab = abs(encrypt);
 ab(ab<50) = 0;
 imagesc(ab);
