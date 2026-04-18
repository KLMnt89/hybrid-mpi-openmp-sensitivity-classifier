"""
run_benchmark.py
================
Главен benchmark скрипт со реални податоци (GovDocs1 + Enron)

Опции:
1. Benchmark (спореди Sequential, MPI, OpenMP, Hybrid)
2. Избор на број на датотеки
3. Генерирање на графици и извештаи
"""

import os
import sys
import time
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Import real file loader
from real_file_loader import RealFileLoader

# Import experiments
from experiments.sequential_baseline import run_sequential_experiment
from experiments.mpi_only import run_mpi_only_experiment
from experiments.openmp_only import run_openmp_only_experiment
from experiments.hybrid_mpi_openmp import run_hybrid_experiment

# Import metrics
from src.utils.metrics import calculate_speedup, calculate_efficiency, calculate_classification_accuracy


def run_full_benchmark(num_files: int = 100):
    """
    Complete benchmark со реални податоци

    Args:
        num_files: Број на датотеки за тестирање
    """
    print("\n" + "=" * 80)
    print("🔬 HYBRID MPI-OPENMP FILE CLASSIFICATION - FULL BENCHMARK")
    print("=" * 80)
    print(f"Dataset: GovDocs1 Corpus (real government documents)")
    print(f"Files to test: {num_files}")
    print("=" * 80)

    # ========================================
    # 1. LOAD REAL FILES
    # ========================================
    print("\n📂 Loading real files from GovDocs1...")

    loader = RealFileLoader()
    govdocs_path = Path("datasets/govdocs1/000")

    if not govdocs_path.exists():
        print(f"❌ ERROR: GovDocs1 not found at {govdocs_path}")
        print("Please ensure datasets are extracted properly.")
        sys.exit(1)

    files = loader.load_from_directory(str(govdocs_path), max_files=num_files)

    if len(files) < 10:
        print(f"❌ ERROR: Too few files loaded ({len(files)}). Need at least 10.")
        sys.exit(1)

    print(f"✓ Loaded {len(files)} real files")
    print(f"  Average size: {sum(f.size for f in files) / len(files) / 1024:.1f} KB")

    # ========================================
    # 2. RUN EXPERIMENTS
    # ========================================
    print("\n" + "=" * 80)
    print("🧪 RUNNING EXPERIMENTS")
    print("=" * 80)

    all_results = []

    # Sequential Baseline
    print("\n[1/8] Sequential Baseline")
    print("-" * 80)
    seq_results, seq_time = run_sequential_experiment(files)

    # Classification accuracy
    accuracy_stats = calculate_classification_accuracy(seq_results)

    all_results.append({
        'approach': 'Sequential',
        'processes': 1,
        'threads': 1,
        'time': seq_time,
        'speedup': 1.0,
        'efficiency': 1.0,
        'throughput': len(files) / seq_time
    })

    # MPI-only experiments
    print("\n[2/8] MPI-only Experiments")
    print("-" * 80)

    for P in [2, 4, 8]:
        mpi_results, mpi_time = run_mpi_only_experiment(files, num_processes=P)

        speedup = calculate_speedup(seq_time, mpi_time)
        efficiency = calculate_efficiency(speedup, P)

        print(f"  P={P}: Speedup={speedup:.2f}x, Efficiency={efficiency:.1%}")

        all_results.append({
            'approach': 'MPI-only',
            'processes': P,
            'threads': 1,
            'time': mpi_time,
            'speedup': speedup,
            'efficiency': efficiency,
            'throughput': len(files) / mpi_time
        })

    # OpenMP-only experiments
    print("\n[3/8] OpenMP-only Experiments")
    print("-" * 80)

    for T in [2, 4, 8]:
        openmp_results, openmp_time = run_openmp_only_experiment(files, num_threads=T)

        speedup = calculate_speedup(seq_time, openmp_time)
        efficiency = calculate_efficiency(speedup, T)

        print(f"  T={T}: Speedup={speedup:.2f}x, Efficiency={efficiency:.1%}")

        all_results.append({
            'approach': 'OpenMP-only',
            'processes': 1,
            'threads': T,
            'time': openmp_time,
            'speedup': speedup,
            'efficiency': efficiency,
            'throughput': len(files) / openmp_time
        })

    # Hybrid MPI-OpenMP experiments
    print("\n[4/8] Hybrid MPI-OpenMP Experiments")
    print("-" * 80)

    for P in [2, 4, 8]:
        for T in [2, 4]:
            hybrid_results, hybrid_time = run_hybrid_experiment(files, num_processes=P, num_threads=T)

            speedup = calculate_speedup(seq_time, hybrid_time)
            total_procs = P * T
            efficiency = calculate_efficiency(speedup, total_procs)

            print(f"  P={P}, T={T}: Speedup={speedup:.2f}x, Efficiency={efficiency:.1%}")

            all_results.append({
                'approach': 'Hybrid',
                'processes': P,
                'threads': T,
                'time': hybrid_time,
                'speedup': speedup,
                'efficiency': efficiency,
                'throughput': len(files) / hybrid_time
            })

    # ========================================
    # 3. SAVE RESULTS
    # ========================================
    print("\n" + "=" * 80)
    print("💾 SAVING RESULTS")
    print("=" * 80)

    # Create results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    # Save CSV
    df = pd.DataFrame(all_results)
    csv_path = results_dir / "benchmark_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ Saved: {csv_path}")

    # ========================================
    # 4. GENERATE PLOTS
    # ========================================
    print("\n📊 Generating visualizations...")

    generate_plots(df, results_dir, len(files))

    # ========================================
    # 5. GENERATE SUMMARY
    # ========================================
    generate_summary_report(df, results_dir, len(files), accuracy_stats, seq_time)

    # ========================================
    # 6. FINAL SUMMARY
    # ========================================
    print("\n" + "=" * 80)
    print("✅ BENCHMARK COMPLETE!")
    print("=" * 80)

    # Find best configuration
    best = max(all_results[1:], key=lambda x: x['speedup'])

    print(f"\n🏆 BEST CONFIGURATION:")
    print(f"   Approach: {best['approach']}")
    print(f"   P={best['processes']}, T={best['threads']}")
    print(f"   Speedup: {best['speedup']:.2f}x")
    print(f"   Efficiency: {best['efficiency']:.1%}")
    print(f"   Time: {best['time']:.2f}s (vs {seq_time:.2f}s sequential)")

    print(f"\n📁 Generated files in results/:")
    print(f"   - benchmark_results.csv")
    print(f"   - speedup_chart.png")
    print(f"   - efficiency_plot.png")
    print(f"   - time_comparison.png")
    print(f"   - throughput_comparison.png")
    print(f"   - summary_report.txt")

    print("\n🎓 Ready for your research paper!")


def generate_plots(df: pd.DataFrame, output_dir: Path, num_files: int):
    """Generate all visualization plots"""

    # Боја палета
    colors = {
        'Sequential': '#6C757D',
        'MPI-only': '#2E86AB',
        'OpenMP-only': '#F18F01',
        'Hybrid': '#A23B72'
    }

    # ==========================================
    # Plot 1: Speedup vs Processing Units
    # ==========================================
    plt.figure(figsize=(12, 7))

    # Sequential baseline
    plt.axhline(y=1.0, color='gray', linestyle='--',
                label='Sequential Baseline', linewidth=2.5, alpha=0.7)

    # MPI-only
    mpi_data = df[df['approach'] == 'MPI-only'].sort_values('processes')
    plt.plot(mpi_data['processes'], mpi_data['speedup'],
             'o-', linewidth=3, markersize=10,
             label='MPI-only (Distributed Memory)',
             color=colors['MPI-only'])

    # Add value labels
    for _, row in mpi_data.iterrows():
        plt.text(row['processes'], row['speedup'] + 0.15,
                f"{row['speedup']:.2f}x",
                ha='center', fontsize=9, fontweight='bold')

    # OpenMP-only
    openmp_data = df[df['approach'] == 'OpenMP-only'].sort_values('threads')
    plt.plot(openmp_data['threads'], openmp_data['speedup'],
             '^-', linewidth=3, markersize=10,
             label='OpenMP-only (Shared Memory)',
             color=colors['OpenMP-only'])

    for _, row in openmp_data.iterrows():
        plt.text(row['threads'], row['speedup'] + 0.15,
                f"{row['speedup']:.2f}x",
                ha='center', fontsize=9, fontweight='bold')

    # Hybrid (T=4) - Best case
    hybrid_t4 = df[(df['approach'] == 'Hybrid') & (df['threads'] == 4)].sort_values('processes')
    hybrid_t4_cores = hybrid_t4['processes'] * hybrid_t4['threads']
    plt.plot(hybrid_t4_cores, hybrid_t4['speedup'],
             's-', linewidth=3, markersize=10,
             label='Hybrid MPI-OpenMP (P×T=4)',
             color=colors['Hybrid'])

    for _, row in hybrid_t4.iterrows():
        cores = row['processes'] * row['threads']
        plt.text(cores, row['speedup'] + 0.3,
                f"{row['speedup']:.2f}x\n(P={int(row['processes'])},T={int(row['threads'])})",
                ha='center', fontsize=8, fontweight='bold')

    plt.xlabel('Number of Processing Units', fontsize=13, fontweight='bold')
    plt.ylabel('Speedup Factor (S)', fontsize=13, fontweight='bold')
    plt.title(f'Performance Speedup Comparison\n({num_files} Real Files from GovDocs1 Corpus)',
              fontsize=15, fontweight='bold', pad=20)
    plt.legend(fontsize=11, loc='upper left', framealpha=0.95)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(output_dir / 'speedup_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ speedup_chart.png")

    # ==========================================
    # Plot 2: Parallel Efficiency
    # ==========================================
    plt.figure(figsize=(12, 7))

    plt.axhline(y=1.0, color='green', linestyle='--',
                label='Ideal Efficiency (100%)', linewidth=2.5, alpha=0.7)
    plt.axhline(y=0.80, color='orange', linestyle=':',
                label='Strong Scaling Threshold (80%)', linewidth=2, alpha=0.6)
    plt.axhline(y=0.60, color='red', linestyle=':',
                label='Acceptable Threshold (60%)', linewidth=2, alpha=0.6)

    # MPI-only efficiency
    mpi_eff = df[df['approach'] == 'MPI-only'].sort_values('processes')
    plt.plot(mpi_eff['processes'], mpi_eff['efficiency'],
             'o-', linewidth=3, markersize=10,
             label='MPI-only',
             color=colors['MPI-only'])

    # OpenMP-only efficiency
    openmp_eff = df[df['approach'] == 'OpenMP-only'].sort_values('threads')
    plt.plot(openmp_eff['threads'], openmp_eff['efficiency'],
             '^-', linewidth=3, markersize=10,
             label='OpenMP-only',
             color=colors['OpenMP-only'])

    # Hybrid efficiency (by total cores)
    hybrid_data = df[df['approach'] == 'Hybrid'].copy()
    hybrid_data['total_cores'] = hybrid_data['processes'] * hybrid_data['threads']
    hybrid_grouped = hybrid_data.groupby('total_cores')['efficiency'].mean().sort_index()
    plt.plot(hybrid_grouped.index, hybrid_grouped.values,
             's-', linewidth=3, markersize=10,
             label='Hybrid MPI-OpenMP (average)',
             color=colors['Hybrid'])

    plt.xlabel('Number of Processing Units', fontsize=13, fontweight='bold')
    plt.ylabel('Parallel Efficiency', fontsize=13, fontweight='bold')
    plt.title(f'Parallel Efficiency Analysis\n({num_files} Files)',
              fontsize=15, fontweight='bold', pad=20)
    plt.legend(fontsize=11, loc='upper right', framealpha=0.95)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.ylim(0, 1.05)

    # Add percentage labels
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

    plt.tight_layout()
    plt.savefig(output_dir / 'efficiency_plot.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ efficiency_plot.png")

    # ==========================================
    # Plot 3: Execution Time Comparison (Bar Chart)
    # ==========================================
    plt.figure(figsize=(12, 7))

    # Prepare data for comparison
    approaches_data = [
        ('Sequential', df[df['approach'] == 'Sequential']['time'].values[0]),
        ('MPI-only\n(P=4)', df[(df['approach'] == 'MPI-only') & (df['processes'] == 4)]['time'].values[0]),
        ('OpenMP-only\n(T=4)', df[(df['approach'] == 'OpenMP-only') & (df['threads'] == 4)]['time'].values[0]),
        ('Hybrid\n(P=4,T=4)', df[(df['approach'] == 'Hybrid') & (df['processes'] == 4) & (df['threads'] == 4)]['time'].values[0])
    ]

    labels = [a[0] for a in approaches_data]
    times = [a[1] for a in approaches_data]
    bar_colors = [colors['Sequential'], colors['MPI-only'], colors['OpenMP-only'], colors['Hybrid']]

    bars = plt.bar(labels, times, color=bar_colors, alpha=0.85, edgecolor='black', linewidth=2)

    # Add value labels and speedup on bars
    seq_time = times[0]
    for i, (bar, time_val) in enumerate(zip(bars, times)):
        height = bar.get_height()
        speedup = seq_time / time_val

        # Time label
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02 * max(times),
                f'{time_val:.2f}s',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

        # Speedup label (skip for sequential)
        if i > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height/2,
                    f'{speedup:.2f}× faster',
                    ha='center', va='center', fontsize=10,
                    fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7))

    plt.ylabel('Execution Time (seconds)', fontsize=13, fontweight='bold')
    plt.title(f'Processing Time Comparison\n({num_files} Real Government Documents)',
              fontsize=15, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, axis='y', linestyle='--')
    plt.tight_layout()
    plt.savefig(output_dir / 'time_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ time_comparison.png")

    # ==========================================
    # Plot 4: Throughput Comparison
    # ==========================================
    plt.figure(figsize=(12, 7))

    throughputs = [num_files / t for t in times]
    bars = plt.bar(labels, throughputs, color=bar_colors, alpha=0.85, edgecolor='black', linewidth=2)

    # Add value labels
    for bar, tp in zip(bars, throughputs):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + max(throughputs) * 0.02,
                f'{tp:.1f}\nfiles/s',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.ylabel('Throughput (files per second)', fontsize=13, fontweight='bold')
    plt.title(f'Classification Throughput Comparison\n({num_files} Files)',
              fontsize=15, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, axis='y', linestyle='--')
    plt.tight_layout()
    plt.savefig(output_dir / 'throughput_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ throughput_comparison.png")


def generate_summary_report(df: pd.DataFrame, output_dir: Path, num_files: int,
                            accuracy_stats: dict, seq_time: float):
    """Generate text summary report"""

    report_path = output_dir / "summary_report.txt"

    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("PERFORMANCE SUMMARY REPORT\n")
        f.write("Hybrid MPI-OpenMP File Classification System\n")
        f.write("=" * 80 + "\n\n")

        f.write("DATASET:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Source: GovDocs1 Corpus (real government documents)\n")
        f.write(f"Files tested: {num_files}\n")
        f.write(f"Sequential baseline: {seq_time:.2f}s\n\n")

        # Best configurations
        best_hybrid = df[df['approach'] == 'Hybrid'].nlargest(1, 'speedup').iloc[0]
        best_mpi = df[df['approach'] == 'MPI-only'].nlargest(1, 'speedup').iloc[0]
        best_openmp = df[df['approach'] == 'OpenMP-only'].nlargest(1, 'speedup').iloc[0]

        f.write("BEST CONFIGURATIONS:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Best Hybrid:      P={int(best_hybrid['processes'])}, T={int(best_hybrid['threads'])}, "
                f"Speedup={best_hybrid['speedup']:.2f}x, Efficiency={best_hybrid['efficiency']:.1%}\n")
        f.write(f"Best MPI-only:    P={int(best_mpi['processes'])}, "
                f"Speedup={best_mpi['speedup']:.2f}x, Efficiency={best_mpi['efficiency']:.1%}\n")
        f.write(f"Best OpenMP-only: T={int(best_openmp['threads'])}, "
                f"Speedup={best_openmp['speedup']:.2f}x, Efficiency={best_openmp['efficiency']:.1%}\n\n")

        # Detailed results
        f.write("DETAILED RESULTS:\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Approach':<15} {'P':<5} {'T':<5} {'Time(s)':<10} {'Speedup':<10} {'Efficiency':<12}\n")
        f.write("-" * 80 + "\n")

        for _, row in df.iterrows():
            f.write(f"{row['approach']:<15} {int(row['processes']):<5} {int(row['threads']):<5} "
                    f"{row['time']:<10.2f} {row['speedup']:<10.2f}x {row['efficiency']:<12.1%}\n")

        # Classification distribution
        f.write("\n" + "=" * 80 + "\n")
        f.write("CLASSIFICATION DISTRIBUTION:\n")
        f.write("-" * 80 + "\n")

        for level, stats in accuracy_stats['distribution'].items():
            f.write(f"{level:<15} {stats['count']:>4} ({stats['percentage']:>5.1f}%)\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("NOTE: Results from REAL data (GovDocs1 Corpus)\n")
        f.write("Suitable for research paper Section IV (Results)\n")
        f.write("=" * 80 + "\n")

    print(f"  ✓ summary_report.txt")


def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("🚀 HYBRID MPI-OPENMP FILE CLASSIFICATION BENCHMARK")
    print("=" * 80)

    print("\nHow many files do you want to test?")
    print("  1) 50 files    (quick test - 2-3 minutes)")
    print("  2) 100 files   (standard - 5-8 minutes)")
    print("  3) 500 files   (thorough - 20-30 minutes)")
    print("  4) 1000 files  (paper results - 40-60 minutes)")

    choice = input("\nSelect option (1-4): ").strip()

    num_files_map = {
        '1': 50,
        '2': 100,
        '3': 500,
        '4': 1000
    }

    num_files = num_files_map.get(choice, 100)

    print(f"\n✓ Selected: {num_files} files")

    # Run benchmark
    run_full_benchmark(num_files)


if __name__ == "__main__":
    main()