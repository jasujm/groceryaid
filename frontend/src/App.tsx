import React from "react";
import Container from "react-bootstrap/Container";

import StorePicker from "./components/StorePicker";

import "./App.scss";

function App() {
  const [store, setStore] = React.useState("");

  return (
    <Container>
      <h1>Grocery Aid</h1>
      <StorePicker onChange={setStore} value={store} />
      <p>{store}</p>
    </Container>
  );
}

export default App;
