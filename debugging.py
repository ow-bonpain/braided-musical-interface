import serial
import pygame
import time
import sys
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import threading

print("Imports successful!")

# Initialize pygame mixer for sound
print("Initializing pygame...")
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
print("Pygame initialized!")

# Load sound files
try:
    piccoloC = pygame.mixer.Sound('rhodes_loop.wav')
    tubaC = pygame.mixer.Sound('tuba_c.wav')
    erhu = pygame.mixer.Sound('erhu.wav')
    print("✓ Sounds loaded!")
except Exception as e:
    print(f"✗ ERROR: Could not load sound file: {e}")
    sys.exit(1)

# Configure serial port
PORT = 'COM7'
BAUD_RATE = 9600

try:
    arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)
    print(f"✓ Connected to Arduino on {PORT}")
    time.sleep(2)
    arduino.reset_input_buffer()
except Exception as e:
    print(f"✗ ERROR: Could not connect to Arduino: {e}")
    sys.exit(1)

print("\n--- Audio Visualizer Started ---\n")

# Track touch and playback states
a_playing = False
b_playing = False

# Animation parameters
time_counter = 0
base_radius_a = 0.2
base_radius_b = 0.3
pulse_a = 0
pulse_b = 0

# Setup matplotlib with clean, minimal design
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Remove axes, ticks, and labels for clean look
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_aspect('equal')
ax.axis('off')

# Create circles - now positioned to overlap in center
circle_a = Circle((-0.3, 0), base_radius_a, color='#00ff88', alpha=0.0, linewidth=0, fill=True)
circle_b = Circle((0.3, 0), base_radius_b, color='#ff00ff', alpha=0.0, linewidth=0, fill=True)
circle_overlap = Circle((0, 0), 0.1, color='#ffaa00', alpha=0.0, linewidth=0, fill=True)  # Orange overlap

ax.add_patch(circle_a)
ax.add_patch(circle_b)
ax.add_patch(circle_overlap)

# Add labels with modern font
text_a = ax.text(-0.3, 1.5, 'SENSOR A', ha='center', va='center', 
                 fontsize=22, color='#00ff88', alpha=0.0, weight='bold',
                 fontfamily='sans-serif', fontstyle='normal')
text_b = ax.text(0.3, 1.5, 'SENSOR B', ha='center', va='center',
                 fontsize=22, color='#ff00ff', alpha=0.0, weight='bold',
                 fontfamily='sans-serif', fontstyle='normal')
text_both = ax.text(0, -1.5, 'B O T H   P L A Y I N G', ha='center', va='center',
                    fontsize=26, color='#ffaa00', alpha=0.0, weight='bold',
                    fontfamily='sans-serif', fontstyle='normal')

def update_visualization(frame):
    """Update circles with rhythm-based pulsing and overlap color"""
    global time_counter, pulse_a, pulse_b, a_playing, b_playing
    
    time_counter += 1
    
    # Sensor A (Piccolo) - faster rhythm
    if a_playing:
        pulse_a = 0.4 + 0.3 * np.sin(time_counter * 0.3)  # Fast pulse
        target_radius_a = base_radius_a + pulse_a
        target_alpha_a = 0.7
        text_a_alpha = 0.9
    else:
        target_radius_a = base_radius_a * 0.5
        target_alpha_a = 0.1
        text_a_alpha = 0.2
    
    # Sensor B (Tuba) - slower, deeper rhythm
    if b_playing:
        pulse_b = 0.5 + 0.4 * np.sin(time_counter * 0.15)  # Slow, deep pulse
        target_radius_b = base_radius_b + pulse_b
        target_alpha_b = 0.7
        text_b_alpha = 0.9
    else:
        target_radius_b = base_radius_b * 0.5
        target_alpha_b = 0.1
        text_b_alpha = 0.2
    
    # Overlap circle (appears only when both are playing)
    if a_playing and b_playing:
        # Combine both pulses for dynamic overlap
        combined_pulse = 0.6 + 0.3 * np.sin(time_counter * 0.22)
        target_radius_overlap = (base_radius_a + base_radius_b) * 0.5 + combined_pulse
        target_alpha_overlap = 0.85
        text_both_alpha = 1.0
    else:
        target_radius_overlap = 0.1
        target_alpha_overlap = 0.0
        text_both_alpha = 0.0
    
    # Smooth transitions
    current_radius_a = circle_a.radius
    current_radius_b = circle_b.radius
    current_radius_overlap = circle_overlap.radius
    
    circle_a.set_radius(current_radius_a + (target_radius_a - current_radius_a) * 0.2)
    circle_b.set_radius(current_radius_b + (target_radius_b - current_radius_b) * 0.2)
    circle_overlap.set_radius(current_radius_overlap + (target_radius_overlap - current_radius_overlap) * 0.2)
    
    circle_a.set_alpha(target_alpha_a)
    circle_b.set_alpha(target_alpha_b)
    circle_overlap.set_alpha(target_alpha_overlap)
    
    text_a.set_alpha(text_a_alpha)
    text_b.set_alpha(text_b_alpha)
    text_both.set_alpha(text_both_alpha)
    
    return circle_a, circle_b, circle_overlap, text_a, text_b, text_both

def serial_listener():
    """Background thread to listen for Arduino serial data"""
    global a_playing, b_playing, c_playing
    
    try:
        while True:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                print(f"[DEBUG] Received: '{line}'")

                if line == "Sensor A touched!" or ("A" in line and "touched" in line):
                    if not a_playing:
                        print("🎵 Playing A sound (piccolo)")
                        piccoloC.play(loops=-1)
                        a_playing = True

                elif line == "Sensor B touched!" or ("B" in line and "touched" in line):
                    if not b_playing:
                        print("🎵 Playing B sound (tuba)")
                        tubaC.play(loops=-1)
                        b_playing = True
                
                elif "C" in line:
                    if not c_playing:
                        print("🎵 Playing C sound (erhu)")
                        erhu.play(loops=-1)
                        c_playing = True

                elif line == "Sensors A and B touched!" or ("A and B" in line and "touched" in line):
                    print("🎼 Both sensors touched")

                elif line == "RELEASE A" or ("RELEASE" in line and "A" in line):
                    if a_playing:
                        print("🔇 Stopping A sound")
                        piccoloC.stop()
                        a_playing = False

                elif line == "RELEASE B" or ("RELEASE" in line and "B" in line):
                    if b_playing:
                        print("🔇 Stopping B sound")
                        tubaC.stop()
                        b_playing = False
                
                elif ("RELEASE" in line and "C" in line):
                    if c_playing:
                        print("🔇 Stopping C sound")
                        erhu.stop()
                        c_playing = False

            time.sleep(0.01)
            
    except Exception as e:
        print(f"Serial listener error: {e}")

# Start serial listener in background thread
listener_thread = threading.Thread(target=serial_listener, daemon=True)
listener_thread.start()

print("Starting visualization window...")
print("If the window doesn't appear, check your taskbar or press Alt+Tab")

# Start animation
try:
    ani = FuncAnimation(fig, update_visualization, interval=33, blit=True, cache_frame_data=False)
    print("Animation created, showing plot...")
    plt.show()
    print("Plot window closed")
except Exception as e:
    print(f"ERROR creating animation: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\n--- Exiting ---")
    if a_playing:
        piccoloC.stop()
    if b_playing:
        tubaC.stop()
    arduino.close()
    pygame.quit()