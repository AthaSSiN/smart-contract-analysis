contract C {
	function f(address payable a) public {
		a.transfer(200);
	}
}
