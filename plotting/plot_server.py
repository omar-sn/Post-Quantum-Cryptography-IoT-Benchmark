import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the server timings data
server_file_path = "server_timings.csv"  # Update with your file path
server_timings_df = pd.read_csv(server_file_path)

# Select the relevant numeric columns
numeric_columns = ['Server Hash Time', 'Verify Time', 'Decapsulation Time', 'Decrypt Time']

# Create a directory to save the plots
output_folder = "serverPlots"
os.makedirs(output_folder, exist_ok=True)

# Function to create and save a single plot with readable y-axis formatting and error bars
def plot_metric(data, errors, xlabel, ylabel, title, output_filename, max_error_ratio=0.5):
    # Sort the data in ascending order
    sorted_indices = data.sort_values().index
    data = data.loc[sorted_indices]
    errors = errors.loc[sorted_indices]

    # Cap the error values to prevent extreme error bars
    capped_errors = errors.clip(upper=max_error_ratio * data.max())

    fig, ax = plt.subplots(figsize=(12, 8))
    data.plot(kind='bar', yerr=capped_errors, capsize=4, ax=ax, alpha=0.7, color='skyblue', ecolor='red', error_kw={'elinewidth': 1.5})

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    
    # Extend title with standard deviation text on a new line
    extended_title = f"{title}\nWith Standard deviation"
    ax.set_title(extended_title, fontsize=16)
    
    ax.set_xticklabels(data.index, rotation=45, ha='right', fontsize=10)
    
    # Format the y-axis to use commas for large numbers
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    plt.close()
    print(f"Saved plot: {output_filename}")


def main():
    # Loop through each device and generate plots
    for device in server_timings_df['Device Name'].unique():
        device_data = server_timings_df[server_timings_df['Device Name'] == device]
        device_output_folder = os.path.join(output_folder, device.replace(" ", "_"))
        os.makedirs(device_output_folder, exist_ok=True)

        # Calculate averages and standard deviations for metrics by KEM Algorithm
        kem_stats = device_data.groupby('KEM Algorithm')[numeric_columns].agg(['mean', 'std'])

        # Calculate Verify Time statistics by Signature Algorithm
        signature_stats = device_data.groupby('Signature Algorithm')['Verify Time'].agg(['mean', 'std'])

        # Separate Rainbow Classic algorithms for Verify Time
        rainbow_classic_algorithms = signature_stats[signature_stats.index.str.contains('rainbow')]
        non_rainbow_algorithms = signature_stats[~signature_stats.index.str.contains('rainbow')]

        # Separate Kyber algorithms for Decapsulation Time
        kyber_algorithms = kem_stats[kem_stats.index.str.contains('kyber')]
        non_kyber_algorithms = kem_stats[~kem_stats.index.str.contains('kyber')]

        # Plot Decapsulation Time with Kyber and Non-Kyber separated
        plot_metric(
            non_kyber_algorithms[('Decapsulation Time', 'mean')],
            errors=non_kyber_algorithms[('Decapsulation Time', 'std')],
            xlabel='KEM Algorithm',
            ylabel='Decapsulation Time (microseconds)',
            title=f'Average Decapsulation Time by KEM Algorithm (Non-Kyber) - {device}',
            output_filename=os.path.join(device_output_folder, 'avg_decapsulation_time_by_kem_non_kyber.png'),
        )

        plot_metric(
            kyber_algorithms[('Decapsulation Time', 'mean')],
            errors=kyber_algorithms[('Decapsulation Time', 'std')],
            xlabel='KEM Algorithm',
            ylabel='Decapsulation Time (microseconds)',
            title=f'Average Decapsulation Time by KEM Algorithm (Kyber) - {device}',
            output_filename=os.path.join(device_output_folder, 'avg_decapsulation_time_by_kem_kyber.png'),
        )

        # Plot Verify Time with Rainbow and Non-Rainbow separated
        plot_metric(
            non_rainbow_algorithms['mean'],
            errors=non_rainbow_algorithms['std'],
            xlabel='Signature Algorithm',
            ylabel='Verify Time (microseconds)',
            title=f'Average Verify Time by Non-Rainbow Signature Algorithms - {device}',
            output_filename=os.path.join(device_output_folder, 'avg_verify_time_by_non_rainbow_signature.png'),
        )

        plot_metric(
            rainbow_classic_algorithms['mean'],
            errors=rainbow_classic_algorithms['std'],
            xlabel='Signature Algorithm',
            ylabel='Verify Time (microseconds)',
            title=f'Average Verify Time by Rainbow Signature Algorithms - {device}',
            output_filename=os.path.join(device_output_folder, 'avg_verify_time_by_rainbow_signature.png'),
        )

        # Plot other metrics (Server Hash Time and Decrypt Time) by KEM Algorithm
        for metric in ['Server Hash Time', 'Decrypt Time']:
            plot_metric(
                kem_stats[(metric, 'mean')],
                errors=kem_stats[(metric, 'std')],
                xlabel='KEM Algorithm',
                ylabel=f'{metric} (microseconds)',
                title=f'Average {metric} by KEM Algorithm - {device}',
                output_filename=os.path.join(device_output_folder, f'avg_{metric.lower().replace(" ", "_")}_by_kem.png'),
            )


if __name__ == "__main__":
    main()
