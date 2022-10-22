pragma solidity ^0.8.6;

interface Unknown {
	function callMe() external;
}

contract ExtCall {
	uint x;

	function setX(uint y) public {
		x = y;
	}

	function xMut(Unknown u) public {
		uint x_prev = x;
		u.callMe();
		// Can `x` change?
		assert(x_prev == x);
	}
}
