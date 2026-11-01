// Prints the version and nothing else until the engine exists.
fn main() {
    println!("sauro {}", env!("CARGO_PKG_VERSION"));
}
