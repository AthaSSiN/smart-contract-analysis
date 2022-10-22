contract C {
	uint sum = msg.value;
	function f() public payable {
		sum += msg.value;
	}
	function inv() public view {
		assert(address(this).balance == sum); // should fail
		assert(address(this).balance >= sum); // should hold
	}
}
