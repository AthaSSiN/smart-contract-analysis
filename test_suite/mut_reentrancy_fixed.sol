// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.6;

interface Unknown {
	function callme() external;
}

contract ExtCall {
	uint x;

	bool lock;
	modifier mutex {
		require(!lock);
		lock = true;
		_;
		lock = false;
	}

	function setX(uint y) mutex public {
		x = y;
	}

	function xMut(Unknown u) mutex public {
		uint x_prev = x;
		u.callme();
		assert(x_prev == x);
	}
}

