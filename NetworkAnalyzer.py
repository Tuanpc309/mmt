#!/usr/bin/env python3
"""
Network Performance Analyzer
Analyzes network statistics from HD video streaming tests.
"""

import json
import time
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from datetime import datetime

class NetworkAnalyzer:
    """Analyze and visualize network performance metrics."""
    
    def __init__(self):
        self.test_results = []
        
    def run_analysis_test(self, resolution, duration=30):
        """
        Run a simulated analysis test.
        
        Args:
            resolution: Video resolution (sd, 720p, 1080p)
            duration: Test duration in seconds
        """
        print(f"\n{'='*60}")
        print(f"Network Performance Analysis - {resolution}")
        print(f"{'='*60}\n")
        
        # Simulated test parameters based on resolution
        params = {
            'sd': {'fps': 30, 'frame_size': 8, 'bandwidth': 240, 'latency': 30, 'loss': 0.5},
            '720p': {'fps': 30, 'frame_size': 50, 'bandwidth': 1500, 'latency': 60, 'loss': 1.5},
            '1080p': {'fps': 30, 'frame_size': 120, 'bandwidth': 3600, 'latency': 100, 'loss': 2.5},
        }
        
        if resolution not in params:
            print(f"Unknown resolution: {resolution}")
            return None
        
        p = params[resolution]
        
        # Generate test results
        results = {
            'resolution': resolution,
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'frames_sent': p['fps'] * duration,
            'frames_received': int(p['fps'] * duration * (1 - p['loss']/100)),
            'avg_frame_size_kb': p['frame_size'],
            'bandwidth_kbps': p['bandwidth'],
            'avg_latency_ms': p['latency'],
            'jitter_ms': p['latency'] * 0.1,
            'packet_loss_rate': p['loss'],
        }
        
        results['frames_lost'] = results['frames_sent'] - results['frames_received']
        results['frame_loss_rate'] = (results['frames_lost'] / results['frames_sent']) * 100
        results['total_data_mb'] = (results['frames_sent'] * results['avg_frame_size_kb']) / 1024
        
        # Calculate fragmentation
        mtu_payload = 1384  # bytes
        results['fragments_per_frame'] = max(1, int((results['avg_frame_size_kb'] * 1024) / mtu_payload))
        results['total_fragments'] = results['frames_sent'] * results['fragments_per_frame']
        
        self.test_results.append(results)
        return results
    
    def print_results(self, results):
        """Print analysis results in a formatted way."""
        print(f"Test Duration: {results['duration']} seconds")
        print(f"\nVideo Metrics:")
        print(f"  Resolution: {results['resolution']}")
        print(f"  Average Frame Size: {results['avg_frame_size_kb']:.2f} KB")
        print(f"  Frames Sent: {results['frames_sent']}")
        print(f"  Frames Received: {results['frames_received']}")
        print(f"  Frames Lost: {results['frames_lost']}")
        print(f"  Frame Loss Rate: {results['frame_loss_rate']:.2f}%")
        
        print(f"\nFragmentation:")
        print(f"  Fragments per Frame: {results['fragments_per_frame']}")
        print(f"  Total Fragments: {results['total_fragments']}")
        print(f"  Fragmentation Needed: {'YES' if results['fragments_per_frame'] > 1 else 'NO'}")
        
        print(f"\nNetwork Performance:")
        print(f"  Bandwidth: {results['bandwidth_kbps']:.0f} Kbps ({results['bandwidth_kbps']/1024:.2f} Mbps)")
        print(f"  Total Data: {results['total_data_mb']:.2f} MB")
        print(f"  Average Latency: {results['avg_latency_ms']:.2f} ms")
        print(f"  Jitter: {results['jitter_ms']:.2f} ms")
        print(f"  Packet Loss Rate: {results['packet_loss_rate']:.2f}%")
        
        # Performance assessment
        print(f"\nPerformance Assessment:")
        if results['frame_loss_rate'] < 1:
            quality = "EXCELLENT"
        elif results['frame_loss_rate'] < 3:
            quality = "GOOD"
        elif results['frame_loss_rate'] < 5:
            quality = "FAIR"
        else:
            quality = "POOR"
        print(f"  Overall Quality: {quality}")
        
        if results['avg_latency_ms'] < 50:
            latency_rating = "EXCELLENT (Real-time capable)"
        elif results['avg_latency_ms'] < 100:
            latency_rating = "GOOD (Suitable for streaming)"
        elif results['avg_latency_ms'] < 200:
            latency_rating = "FAIR (Noticeable delay)"
        else:
            latency_rating = "POOR (High latency)"
        print(f"  Latency: {latency_rating}")
        
    def generate_comparison_report(self):
        """Generate a comparison report for all tests."""
        if not self.test_results:
            print("No test results available.")
            return
        
        print(f"\n{'='*70}")
        print("COMPARATIVE ANALYSIS - ALL RESOLUTIONS")
        print(f"{'='*70}\n")
        
        # Header
        print(f"{'Resolution':<15} {'FPS':<8} {'Size(KB)':<12} {'BW(Mbps)':<12} {'Loss%':<10} {'Latency(ms)':<12}")
        print("-" * 70)
        
        # Data rows
        for result in self.test_results:
            fps = result['frames_received'] / result['duration']
            print(f"{result['resolution']:<15} "
                  f"{fps:<8.1f} "
                  f"{result['avg_frame_size_kb']:<12.1f} "
                  f"{result['bandwidth_kbps']/1024:<12.2f} "
                  f"{result['frame_loss_rate']:<10.2f} "
                  f"{result['avg_latency_ms']:<12.1f}")
        
        print("\n" + "="*70)
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        print("-" * 70)
        
        for result in self.test_results:
            print(f"\n{result['resolution']}:")
            
            # Minimum bandwidth recommendation
            required_bw = result['bandwidth_kbps'] * 1.3  # 30% overhead
            print(f"  Minimum Network Bandwidth: {required_bw/1024:.1f} Mbps")
            
            # Fragmentation impact
            if result['fragments_per_frame'] > 1:
                print(f"  Fragmentation: {result['fragments_per_frame']} fragments/frame")
                print(f"  Impact: Increased packet overhead and potential loss sensitivity")
            else:
                print(f"  Fragmentation: Not required (frame fits in single packet)")
            
            # Use case recommendations
            if result['avg_latency_ms'] < 100 and result['frame_loss_rate'] < 2:
                print(f"  Suitable for: Real-time applications, video conferencing")
            elif result['avg_latency_ms'] < 200 and result['frame_loss_rate'] < 5:
                print(f"  Suitable for: Video streaming, online media")
            else:
                print(f"  Suitable for: Download and play, non-critical streaming")
    
    def save_results(self, filename='network_analysis.json'):
        """Save test results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nResults saved to: {filename}")
    
    def generate_plots(self, output_prefix='network_plot'):
        """Generate visualization plots."""
        if not self.test_results:
            print("No test results to plot.")
            return
        
        print(f"\nGenerating plots...")
        
        # Extract data
        resolutions = [r['resolution'] for r in self.test_results]
        bandwidths = [r['bandwidth_kbps']/1024 for r in self.test_results]
        latencies = [r['avg_latency_ms'] for r in self.test_results]
        loss_rates = [r['frame_loss_rate'] for r in self.test_results]
        fragments = [r['fragments_per_frame'] for r in self.test_results]
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('HD Video Streaming Performance Analysis', fontsize=16, fontweight='bold')
        
        # Bandwidth plot
        ax1.bar(resolutions, bandwidths, color=['green', 'orange', 'red'])
        ax1.set_ylabel('Bandwidth (Mbps)')
        ax1.set_title('Required Bandwidth by Resolution')
        ax1.grid(axis='y', alpha=0.3)
        
        # Latency plot
        ax2.bar(resolutions, latencies, color=['green', 'orange', 'red'])
        ax2.set_ylabel('Latency (ms)')
        ax2.set_title('Average Latency by Resolution')
        ax2.grid(axis='y', alpha=0.3)
        
        # Loss rate plot
        ax3.bar(resolutions, loss_rates, color=['green', 'orange', 'red'])
        ax3.set_ylabel('Frame Loss Rate (%)')
        ax3.set_title('Frame Loss Rate by Resolution')
        ax3.grid(axis='y', alpha=0.3)
        
        # Fragmentation plot
        ax4.bar(resolutions, fragments, color=['green', 'orange', 'red'])
        ax4.set_ylabel('Fragments per Frame')
        ax4.set_title('Fragmentation Requirements')
        ax4.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_file = f"{output_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(plot_file, dpi=150, bbox_inches='tight')
        print(f"Plot saved to: {plot_file}")
        
        plt.close()


def main():
    """Main function to run network analysis."""
    analyzer = NetworkAnalyzer()
    
    print("="*70)
    print("HD VIDEO STREAMING - NETWORK PERFORMANCE ANALYSIS")
    print("="*70)
    
    # Run tests for different resolutions
    test_configs = [
        ('sd', 30),
        ('720p', 30),
        ('1080p', 30),
    ]
    
    for resolution, duration in test_configs:
        results = analyzer.run_analysis_test(resolution, duration)
        if results:
            analyzer.print_results(results)
        time.sleep(0.5)
    
    # Generate comparison report
    analyzer.generate_comparison_report()
    
    # Save results
    analyzer.save_results()
    
    # Generate plots
    try:
        analyzer.generate_plots()
    except Exception as e:
        print(f"\nNote: Could not generate plots: {e}")
        print("Install matplotlib for visualization support: pip install matplotlib")
    
    print(f"\n{'='*70}")
    print("Analysis Complete!")
    print(f"{'='*70}\n")
    
    # Network usage summary
    print("\nNETWORK USAGE SUMMARY:")
    print("-" * 70)
    total_data = sum(r['total_data_mb'] for r in analyzer.test_results)
    total_fragments = sum(r['total_fragments'] for r in analyzer.test_results)
    print(f"Total Data Transmitted: {total_data:.2f} MB")
    print(f"Total Fragments Sent: {total_fragments:,}")
    print(f"Average Packet Loss: {sum(r['packet_loss_rate'] for r in analyzer.test_results) / len(analyzer.test_results):.2f}%")
    
    print("\nKEY FINDINGS:")
    print("-" * 70)
    print("1. HD video requires fragmentation for efficient transmission")
    print("2. Higher resolutions increase bandwidth and latency requirements")
    print("3. Packet loss has greater impact on higher resolutions")
    print("4. MTU-based fragmentation enables smooth HD playback")
    print("5. Network statistics help identify performance bottlenecks")


if __name__ == "__main__":
    main()
