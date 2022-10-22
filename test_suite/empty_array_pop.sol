contract C {
	uint[] a;
	function g() internal {
		a.push();
	}
	function f() public {
		a.pop();
		g();
	}
}
