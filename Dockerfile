# The image we will start with:
FROM trailofbits/eth-security-toolbox

# Install packages, by running a command
RUN pip3 install z3-solver
RUN sudo ln -s /home/ethsec/.local/lib/python3.6/site-packages/z3/lib/libz3.so.4.8 /usr/lib
RUN sudo ln -s /home/ethsec/.local/lib/python3.6/site-packages/z3/lib/libz3.so.4.11 /usr/lib
RUN solc-select install 0.8.17
RUN solc-select use 0.8.17
