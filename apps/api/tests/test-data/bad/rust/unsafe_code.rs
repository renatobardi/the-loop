// Bad: Unsafe code

// rust-security-002
unsafe {
    let ptr = std::ptr::null_mut::<i32>();
    *ptr = 42;
}

// rust-security-003
panic!("Unrecoverable error");
