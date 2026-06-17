import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the sample data
file_path = "client_timings.csv"  # Update this path to your file location
client_timings_df = pd.read_csv(file_path)

# Select only the numeric columns for the mean calculation
numeric_columns = ['Encapsulation Time', 'Encryption Time', 'Client Hash Time', 'Sign Time']

# Create a directory to save the plots
output_folder = "clientPlots"
os.makedirs(output_folder, exist_ok=True)

# Function to create and save a single bar plot with formatted y-axis
def plot_metric(data, metric, xlabel, ylabel, title, output_filename):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Sort data in ascending order
    mean_data = data.sort_values(ascending=True)
    std_dev = client_timings_df.groupby(['KEM Algorithm' if 'KEM' in title else 'Signature Algorithm'])[metric].std()

    # Create bar plot with error bars
    mean_data.plot(kind='bar', ax=ax, alpha=0.7, legend=False)
    
    # Add error bars for sorted data
    x_positions = range(len(mean_data))
    ax.errorbar(x_positions, mean_data, 
                yerr=std_dev[mean_data.index], 
                fmt='none', 
                ecolor='red', 
                capsize=5, 
                capthick=2)

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(f'{title}\nwith Standard Deviation', fontsize=16)

    # Format y-axis with commas for large numbers
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    plt.close()
    print(f"Saved plot: {output_filename}")

    # Print out mean and standard deviation for reference
    print(f"\nMean and Standard Deviation for {metric}:")
    mean_std_df = pd.DataFrame({
        'Mean': mean_data,
        'Std Dev': std_dev[mean_data.index]
    })
    print(mean_std_df)

def main():
    # Loop through each device and generate plots
    for device in client_timings_df['Device Name'].unique():
        device_data = client_timings_df[client_timings_df['Device Name'] == device]
        device_output_folder = os.path.join(output_folder, device.replace(" ", "_"))
        os.makedirs(device_output_folder, exist_ok=True)

        # Calculate average encapsulation, encryption, and hash times by KEM Algorithm
        kem_averages = device_data.groupby('KEM Algorithm')[['Encapsulation Time', 'Encryption Time', 'Client Hash Time']].mean()

        # Calculate average sign times by Signature Algorithm
        signature_averages = device_data.groupby('Signature Algorithm')['Sign Time'].mean()

        # Plot Encapsulation Time, Encryption Time, and Client Hash Time by KEM Algorithm
        for metric in ['Encapsulation Time', 'Encryption Time', 'Client Hash Time']:
            plot_metric(
                kem_averages[metric],
                metric,
                xlabel='KEM Algorithm',
                ylabel=f'{metric} (microseconds)',
                title=f'Average {metric} by KEM Algorithm - {device}',
                output_filename=os.path.join(device_output_folder, f'{metric.lower().replace(" ", "_")}_kem.png'),
            )

        # Plot Sign Time by Signature Algorithm
        plot_metric(
            signature_averages,
            'Sign Time',
            xlabel='Signature Algorithm',
            ylabel='Sign Time (microseconds)',
            title=f'Average Sign Time by Signature Algorithm - {device}',
            output_filename=os.path.join(device_output_folder, 'sign_time_signature.png'),
        )

if __name__ == "__main__":
    main()
