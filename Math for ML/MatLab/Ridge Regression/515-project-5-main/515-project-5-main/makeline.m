function l = makeline(ww,bb,ll,mm,nw)
%  
%  Function to make the line segment
%  of the intersection of the line
%  of equation  (x,y). ww = b with
%  the box defined by y = ll(2) (lower side), x = mm(1) (right side),
%  y = mm(2) (upper side), x = ll(1) (left side)
% nw = ||w||


%  Test where the line of equation  (x,y). w = b
%  intersects the box defined by y = ll(2) (lower side), x = mm(1) (right side),
%  y = mm(2) (upper side), x = ll(1) (left side)

% Normalizes equation of the line with ||w|| = 1.

w = ww/nw; b = bb/nw;
% fprintf('normalized w(1) =  %d \n', w(1))
% fprintf('normalized w(2) =  %d \n', w(2))
% fprintf('normalized b =  %d \n',b)
if abs(w(2)) < 10^(-11)  % vertical line
   p1 = [b/w(1) ll(2)]; p2 = [b/w(1) mm(2)];
else
   if abs(w(1)) < 10^(-11)  % horizontal line
      p1 = [ll(1) b/w(2)]; p2 = [mm(1) b/w(2)];
   else
       xll2 = (b - w(2)*ll(2))/w(1); ymm1 = (b - w(1)*mm(1))/w(2);
       xmm2 = (b - w(2)*mm(2))/w(1); yll1 = (b - w(1)*ll(1))/w(2);
       if ll(1) <= xll2 && xll2 <= mm(1)  % intersects lower side of box
          if ll(2) <= ymm1 && ymm1 <= mm(2) % intersects right side of box
             p1 = [xll2 ll(2)]; p2 = [mm(1) ymm1];             
          else    
              if ll(1) <= xmm2 && xmm2 <= mm(1) % intersects upper side of box
                 p1 = [xll2 ll(2)]; p2 = [xmm2 mm(2)];
              else  % intersects left side of box
                 p1 =[xll2 ll(2)]; p2 = [ll(1) yll1];
              end
          end
       else  % does not intersect lower side of box
          if ll(2) <= ymm1 && ymm1 <= mm(2)  % intersects right side of box
              if ll(1) <= xmm2 && xmm2 <= mm(1) % intersects upper side of box
                 p1 = [mm(1) ymm1]; p2 = [xmm2 mm(2)];
              else  % not lower side, right side, not upper side; intersects 
                    % left side of box
                 p1 =[mm(1),ymm1]; p2 = [ll(1) yll1];
              end
          else % not lower side, not right side; intersects the line x = ll(1) 
               % (left line) and the line y = mm(2) (upper line)  
               p1 = [ll(1) yll1]; p2 = [xmm2 mm(2)]; 
          end
       end
   end
end
l = [p1' p2'];
end

