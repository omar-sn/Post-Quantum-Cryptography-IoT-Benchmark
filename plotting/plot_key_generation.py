import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Create output directory for plots
output_folder = "pqc_plots"
os.makedirs(output_folder, exist_ok=True)

# Read the CSV file
df = pd.read_csv("key_generation_times.csv")

# Convert seconds to microseconds
df['Key Generation Time (μs)'] = df['Key Generation Time'] * 1_000_000

# Set up matplotlib style for professional look
plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'figure.figsize': (16, 8),
    'figure.dpi': 300
})

# Consistent blue color
blue_color = '#3498DB'

def bar_by_algorithm_type():
    # 1. Bar Plot by Algorithm Type
    plt.figure()
    algorithm_type_means = df.groupby('Algorithm Type')['Key Generation Time (μs)'].mean().sort_values(ascending=True)
    algorithm_type_means.plot(kind='bar', color=blue_color, edgecolor='black')
    plt.title('Average Key Generation Times by Algorithm Type', fontweight='bold')
    plt.ylabel('Average Time (microseconds)')
    plt.xlabel('Algorithm Type')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'algorithm_type_comparison.png'))
    plt.close()

def bar_by_algorithm_family():
    # 2. Bar Plot by Algorithm Family
    plt.figure()
    algorithm_family_means = df.groupby('Algorithm Family')['Key Generation Time (μs)'].mean().sort_values(ascending=True)
    algorithm_family_means.plot(kind='bar', color=blue_color, edgecolor='black')
    plt.title('Average Key Generation Times by Algorithm Family', fontweight='bold')
    plt.ylabel('Average Time (microseconds)')
    plt.xlabel('Algorithm Family')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'algorithm_family_comparison.png'))
    plt.close()

def bar_by_device():
    # 3. Bar Plot by Device
    plt.figure()
    device_means = df.groupby('Device')['Key Generation Time (μs)'].mean().sort_values(ascending=True)
    device_means.plot(kind='bar', color=blue_color, edgecolor='black')
    plt.title('Average Key Generation Times by Device', fontweight='bold')
    plt.ylabel('Average Time (microseconds)')
    plt.xlabel('Device')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'device_comparison.png'))
    plt.close()


def sign_algorithms_comp():
    # 4. Comprehensive Signature Algorithms Comparison
    plt.figure(figsize=(20, 10))
    signature_df = df[df['Algorithm Type'] == 'Signature']
    signature_means = signature_df.groupby('Original Algorithm Name')['Key Generation Time (μs)'].mean().sort_values(ascending=True)

    signature_means.plot(kind='bar', color=blue_color, edgecolor='black')
    plt.title('Key Generation Times for All Signature Algorithms', fontweight='bold')
    plt.ylabel('Average Time (microseconds)')
    plt.xlabel('Signature Algorithm')
    plt.xticks(rotation=90, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'all_signature_algorithms.png'))
    plt.close()


def kem_algoithms_comp():
    # 5. Comprehensive KEM Algorithms Comparison
    plt.figure(figsize=(20, 10))
    kem_df = df[df['Algorithm Type'] == 'KEM']
    kem_means = kem_df.groupby('Original Algorithm Name')['Key Generation Time (μs)'].mean().sort_values(ascending=True)

    kem_means.plot(kind='bar', color=blue_color, edgecolor='black')
    plt.title('Key Generation Times for All KEM Algorithms', fontweight='bold')
    plt.ylabel('Average Time (microseconds)')
    plt.xlabel('KEM Algorithm')
    plt.xticks(rotation=90, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'all_kem_algorithms.png'))
    plt.close()


def comp_by_device_and_algo():
    # 6. Comparative Analysis by Device and Algorithm Type
    plt.figure(figsize=(16, 10))
    grouped_means = df.groupby(['Device', 'Algorithm Type'])['Key Generation Time (μs)'].mean().unstack()
    # Sort the index (devices) in ascending order of total mean time
    grouped_means = grouped_means.loc[grouped_means.mean(axis=1).sort_values().index]
    grouped_means.plot(kind='bar', stacked=False, edgecolor='black', color=[blue_color, blue_color])
    plt.title('Average Key Generation Times by Device and Algorithm Type', fontweight='bold')
    plt.ylabel('Average Time (microseconds)')
    plt.xlabel('Device')
    plt.legend(title='Algorithm Type', loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'device_algorithm_type_comparison.png'))
    plt.close()

print("All plots have been generated and saved in the 'pqc_plots' directory.")

if name == "__main__":
    kem_algoithms_comp()
    comp_by_device_and_algo()
    sign_algorithms_comp()
    bar_by_device()
    bar_by_algorithm_family()
    bar_by_algorithm_type()
