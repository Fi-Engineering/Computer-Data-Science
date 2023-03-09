# 515 - Project 2A - Report

#### by Han Yang Lim (hanyangl@seas.upenn.edu) and Alex Newman Ilgenfritz (nailgen@seas.upenn.edu)

## Part 1

Output for part 1 is saved in `/output/part1`.

## Part 2

The results from testing `haar` on vectors `u` and `w` are shown below:

<img src="./figures/part2-u.jpg" alt="graph of u" width="500"/>
<img src="./figures/part2-w.jpg" alt="graph of w" width="500"/>

As seen from above graphs, `u` looks like an instance of the wave but `w` looks like the same wave repeated several times (i.e. having a higher frequency).

## Part 3

The results from using `haar_step` on `w` where `k = 4,5,6,7` are plotted below:

<img src="./figures/part3-w-k-4.jpg" alt="graph of u" width="500"/>
<img src="./figures/part3-w-k-5.jpg" alt="graph of u" width="500"/>
<img src="./figures/part3-w-k-6.jpg" alt="graph of u" width="500"/>
<img src="./figures/part3-w-k-7.jpg" alt="graph of u" width="500"/>

Visual observation of the results show negligible change after performing `haar_step` with k >= 4.
This is because with each successive `haar_step`, only 1/2^k elements in w are modified. As k gets larger, the number of elements in w modified become fewer and fewer, until the graph looks like it has not changed at all.

## Part 4

Output for part 1 is saved in `/output/part4`.

## Part 5

The results of playing Handel after it undergoes `haar_step` transform with k = 0, 1, 2, 3 are below:

<img src="./figures/part-5-handel.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel_hs_1.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel_hs_2.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel_hs_3.jpg" alt="graph of u" width="500"/>

As the waveform undergoes the Haar transform, Handel sounds faster and sounds like it is being played at a higher frequency at the start. But it also starts to sound like several different sound clips stitched together, with the fastest segments at the start and the segments that sound most like the original near the end. The pattern observed here is same as in Part 3, where for increasing levels of k, fewer and fewer elements in Handel undergo the averaging and differencing process until a point where the changes are negligible and cannot really be noticed in a signal from both visual and audio perspective.

After applying `haar` and `haar_inv` on Handel, Handel sounds unchanged. We can view it as a reversible 'compression' algorithm of sorts that processed the audio signal. Again, we see the original Handel audio signal along with Handel after going through `haar` and `haar_inv`. Visually it does not look like an identical reconstruction but from a layman's audio perspective it does not seem to have made a difference.

<img src="./figures/part-5-handel.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-haar-haarinv.jpg" alt="graph of u" width="500"/>

### Other compressions of c1

The original `c1` is shown below after running `haar` on Handel and setting detail coefficients to zero. After that, successive `haar_inv_steps` of varying levels of `k` were performed on `c1`. The sound vectors are plotted below accordingly. From an audio perspective, at the start with low levels of `k`, Handel sounds most clearly as if it is playing at a low bitrate. This progressively improves as `k` is set at higher and higher levels, until it sounds like the original file. Visually, from plotting the vectors we can also see this change, where the most obvious changes take place at the lower levels of `k`, where fewer and fewer changes can be clearly observed at higher levels of `k`.

<img src="./figures/part-5-handel-c1.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k1.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k2.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k3.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k4.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k6.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k8.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k10.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k12.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k14.jpg" alt="graph of u" width="500"/>
<img src="./figures/part-5-handel-c1-k16.jpg" alt="graph of u" width="500"/>