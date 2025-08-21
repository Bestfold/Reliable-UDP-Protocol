struct State {
	name: i32
	parent: State
}

impl State {
	fn enter(&mut self) -> Option<State> {
		None
	}

	fn exit(&mut self) -> Option<State> {
		None
	}

	fn process(&mut self) -> Option<State> {
		None
	}
}

//impl Display for State {}