# IEEE St. Mary’s University Workshops Code Library

Welcome to the official code library for the **IEEE Student Chapter at St. Mary’s University**.  
This repository collects code from our hands-on workshops to support learning and experimentation.  

Here you’ll find:
- **Starter code** — simplified templates for students to begin with.
- **Complete code** — fully working examples, sometimes adapted from or inspired by external projects.
- **External contributions** — when we borrow or adapt code under open-source licenses, we clearly note the source and keep the license files intact.

---

## Workshops

- **Buzzer Workshop**  
  Based on [HiBit’s buzzer repo](https://github.com/hibit-dev/buzzer) (MIT License, © 2022 HiBit).  
  You’ll find both starter and complete versions inside `workshops/buzzer/`.  

- **Robotic Arm Workshop**  
  A hands-on workshop teaching serial-controlled servo robotics using an Arduino Nano and a Python controller. The workshop folder `Robotic Arm/` includes:
  - `servo_test/servo_test.ino` — Arduino sketch to upload
  - `arm.py` and `teleop_keyboard.py` — PC-side controller and API
  - `run_program.py` — student script (edit to write robotic routines)
  - `demos/` — example student programs you can drop in

  Quick start (students):

  ```bash
  cd "Robotic Arm"
  pip install pyserial keyboard
  python teleop_keyboard.py
  # enter COM number when prompted (e.g., 3 for COM3)
  # use WASD + arrow keys to manually control
  # press `t` to run the latest run_program.py (copy from USB)
  ```

---

## Licensing

- All original workshop materials created by the IEEE St. Mary’s University Chapter are licensed under the **MIT License** (see [LICENSE](./LICENSE)).  
- Third-party code (like HiBit’s buzzer) is included under its own license. These are kept in their respective workshop folders.

---

## Contributing

Members are welcome to add starter or complete workshop code.  
When including outside projects:
1. Verify the code has a permissive license (MIT, Apache 2.0, BSD).  
2. Copy the original LICENSE file into the workshop folder.  
3. Add an attribution line in the folder’s README pointing to the source repository.  

This keeps us compliant and respectful of open-source authors.
