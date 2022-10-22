contract C {
	function f(uint256 d) public pure {
		uint x = addmod(1, 2, d);
		assert(x < d);
	}

	function g(uint256 d) public pure {
		uint x = mulmod(1, 2, d);
		assert(x < d);
	}

	function h() public pure returns (uint256) {
		uint x = mulmod(0, 1, 2);
		uint y = mulmod(1, 0, 2);
		assert(x == y);
		uint z = addmod(0, 1, 2);
		uint t = addmod(1, 0, 2);
		assert(z == t);
	}
}
