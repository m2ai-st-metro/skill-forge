// Register-shift probe (Rust): Command arg built with format!.
use std::process::Command;

fn run(user: &str) {
    // probe: interpolated shell argument
    Command::new("sh").arg("-c").arg(format!("convert {}", user));
}
