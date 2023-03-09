function [ll,mm] = showdata(u,v)
%
%  Displays data points 
%
uv = [u, v]; uvp = uv';

%  Finds the smallest x and y coordinates
[xym,I] = min(uvp);
ll = xym;
 ll = ll - 0.5;
%  Finds the largest x and y coordinates
[xyM,J] = max(uvp);
mm = xyM;
mm = mm + 0.5;

%close 
figure
hold on
plot(ll(1),ll(2))
plot(mm(1),mm(2))
plot(u(1,:), u(2,:),'b*')       %  plots blue points
plot(v(1,:), v(2,:),'rx')       %  plots red points
end

