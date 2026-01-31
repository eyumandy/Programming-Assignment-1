import time
import subprocess
import random
import os
import sys

# Try to import matplotlib for graphing
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed. Graphs will not be generated.")
    print("Install with: pip install matplotlib")
    print()


def generate_test_instance(n, seed=None):
    """
    Generates a random test instance of size n.
    """
    if seed is not None:
        random.seed(seed)
    
    lines = [str(n)]
    
    # Hospital preferences
    for _ in range(n):
        prefs = list(range(1, n + 1))
        random.shuffle(prefs)
        lines.append(" ".join(map(str, prefs)))
    
    # Student preferences
    for _ in range(n):
        prefs = list(range(1, n + 1))
        random.shuffle(prefs)
        lines.append(" ".join(map(str, prefs)))
    
    return "\n".join(lines) + "\n"


def measure_matcher_time(n, num_trials=5):
    """
    Measures the average running time of the matcher for problem size n.
    """
    times = []
    
    # Find matcher script
    if os.path.exists('matcher.py'):
        matcher_path = 'matcher.py'
    elif os.path.exists('src/matcher.py'):
        matcher_path = 'src/matcher.py'
    else:
        raise FileNotFoundError("Could not find matcher.py")
    
    for trial in range(num_trials):
        # Generate test instance
        test_input = generate_test_instance(n, seed=n * 100 + trial)
        
        # Write to temporary file
        temp_input = f'temp_input_{n}_{trial}.in'
        with open(temp_input, 'w') as f:
            f.write(test_input)
        
        # Measure time
        start_time = time.time()
        result = subprocess.run(
            ['python', matcher_path, temp_input],
            capture_output=True,
            text=True,
            timeout=60
        )
        end_time = time.time()
        
        # Clean up
        os.remove(temp_input)
        
        if result.returncode == 0:
            times.append(end_time - start_time)
        else:
            print(f"  Warning: Matcher failed for n={n}, trial {trial}")
    
    return sum(times) / len(times) if times else 0


def measure_verifier_time(n, num_trials=5):
    """
    Measures the average running time of the verifier for problem size n.
    """
    times = []
    
    # Find verifier and matcher scripts
    if os.path.exists('verifier.py'):
        verifier_path = 'verifier.py'
        matcher_path = 'matcher.py'
    elif os.path.exists('src/verifier.py'):
        verifier_path = 'src/verifier.py'
        matcher_path = 'src/matcher.py'
    else:
        raise FileNotFoundError("Could not find verifier.py")
    
    for trial in range(num_trials):
        # Generate test instance
        test_input = generate_test_instance(n, seed=n * 100 + trial)
        
        # Write input and generate matching
        temp_input = f'temp_input_{n}_{trial}.in'
        temp_output = f'temp_output_{n}_{trial}.out'
        
        with open(temp_input, 'w') as f:
            f.write(test_input)
        
        # Run matcher to get output
        result = subprocess.run(
            ['python', matcher_path, temp_input],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"  Warning: Matcher failed for n={n}, trial {trial}")
            os.remove(temp_input)
            continue
        
        with open(temp_output, 'w') as f:
            f.write(result.stdout)
        
        # Measure verifier time
        start_time = time.time()
        result = subprocess.run(
            ['python', verifier_path, temp_input, temp_output],
            capture_output=True,
            text=True,
            timeout=60
        )
        end_time = time.time()
        
        # Clean up
        os.remove(temp_input)
        os.remove(temp_output)
        
        if result.returncode == 0:
            times.append(end_time - start_time)
        else:
            print(f"  Warning: Verifier failed for n={n}, trial {trial}")
    
    return sum(times) / len(times) if times else 0


def run_scalability_tests(test_sizes=None, num_trials=5):
    """
    Runs scalability tests for increasing problem sizes.
    """
    if test_sizes is None:
        test_sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    
    print("=" * 80)
    print("SCALABILITY TESTING (Part C)")
    print("=" * 80)
    print(f"\nTesting sizes: {test_sizes}")
    print(f"Trials per size: {num_trials}")
    print()
    
    matcher_times = []
    verifier_times = []
    
    for n in test_sizes:
        print(f"Testing n={n}...")
        
        # Measure matcher time
        print(f"  Measuring matcher performance...")
        matcher_time = measure_matcher_time(n, num_trials)
        matcher_times.append(matcher_time)
        print(f"  ✓ Matcher avg time: {matcher_time:.6f} seconds")
        
        # Measure verifier time
        print(f"  Measuring verifier performance...")
        verifier_time = measure_verifier_time(n, num_trials)
        verifier_times.append(verifier_time)
        print(f"  ✓ Verifier avg time: {verifier_time:.6f} seconds")
        print()
    
    return test_sizes, matcher_times, verifier_times


def plot_results(sizes, matcher_times, verifier_times, output_dir='results'):
    """
    Creates line graphs showing running time vs problem size.
    """
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available. Skipping graph generation.")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Matcher performance
    ax1.plot(sizes, matcher_times, 'b-o', linewidth=2, markersize=8)
    ax1.set_xlabel('Problem Size (n)', fontsize=12)
    ax1.set_ylabel('Running Time (seconds)', fontsize=12)
    ax1.set_title('Matcher Performance', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log', base=2)
    
    # Plot 2: Verifier performance
    ax2.plot(sizes, verifier_times, 'r-o', linewidth=2, markersize=8)
    ax2.set_xlabel('Problem Size (n)', fontsize=12)
    ax2.set_ylabel('Running Time (seconds)', fontsize=12)
    ax2.set_title('Verifier Performance', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log', base=2)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(output_dir, 'scalability_graphs.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graphs saved to: {output_path}")
    
    # Also create combined graph
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, matcher_times, 'b-o', linewidth=2, markersize=8, label='Matcher')
    plt.plot(sizes, verifier_times, 'r-o', linewidth=2, markersize=8, label='Verifier')
    plt.xlabel('Problem Size (n)', fontsize=12)
    plt.ylabel('Running Time (seconds)', fontsize=12)
    plt.title('Algorithm Performance Comparison', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xscale('log', base=2)
    
    combined_path = os.path.join(output_dir, 'combined_graph.png')
    plt.savefig(combined_path, dpi=300, bbox_inches='tight')
    print(f"Combined graph saved to: {combined_path}")
    
    plt.close('all')


def save_results_table(sizes, matcher_times, verifier_times, output_dir='results'):
    """
    Saves results as a formatted table in a text file.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'scalability_results.txt')
    
    with open(output_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("SCALABILITY TEST RESULTS (Part C)\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"{'n':<10} {'Matcher Time (s)':<20} {'Verifier Time (s)':<20}\n")
        f.write("-" * 80 + "\n")
        
        for i, n in enumerate(sizes):
            f.write(f"{n:<10} {matcher_times[i]:<20.6f} {verifier_times[i]:<20.6f}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("OBSERVATIONS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("Matcher Complexity:\n")
        f.write("  - Theoretical: O(n²) in worst case\n")
        f.write("  - Observed trend: ")
        if len(sizes) >= 3:
            # Simple growth rate check
            ratio = matcher_times[-1] / matcher_times[-3] if matcher_times[-3] > 0 else 0
            size_ratio = sizes[-1] / sizes[-3]
            f.write(f"When n increases by {size_ratio}x, time increases by ~{ratio:.1f}x\n")
        f.write("\n")
        
        f.write("Verifier Complexity:\n")
        f.write("  - Theoretical: O(n²) to check all pairs\n")
        f.write("  - Observed trend: ")
        if len(sizes) >= 3:
            ratio = verifier_times[-1] / verifier_times[-3] if verifier_times[-3] > 0 else 0
            size_ratio = sizes[-1] / sizes[-3]
            f.write(f"When n increases by {size_ratio}x, time increases by ~{ratio:.1f}x\n")
    
    print(f"Results table saved to: {output_path}")


def main():
    """
    Main entry point for scalability testing.
    """
    # Change to project root if needed
    if os.path.basename(os.getcwd()) == 'tests':
        os.chdir('..')
    elif os.path.basename(os.getcwd()) == 'src':
        os.chdir('..')
    
    print(f"Running from: {os.getcwd()}\n")
    
    # Run scalability tests
    test_sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    num_trials = 3  # Number of trials to average
    
    sizes, matcher_times, verifier_times = run_scalability_tests(test_sizes, num_trials)
    
    # Save results
    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    print()
    
    save_results_table(sizes, matcher_times, verifier_times)
    plot_results(sizes, matcher_times, verifier_times)
    
    print("\n" + "=" * 80)
    print("SCALABILITY TESTING COMPLETE")
    print("=" * 80)
    print(f"\nResults saved in 'results/' directory")
    print("  - scalability_results.txt (data table)")
    if HAS_MATPLOTLIB:
        print("  - scalability_graphs.png (individual graphs)")
        print("  - combined_graph.png (comparison graph)")
    print()


if __name__ == "__main__":
    main()