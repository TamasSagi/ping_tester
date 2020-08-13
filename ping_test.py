import platform
import subprocess
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from collections import deque
from matplotlib.animation import FuncAnimation


class PingTester( object ):
    """
    This class constantly pings the given host (www.google.com by default) and draws a line graph
    based on the latencies.
    """
    def __init__( self, host="www.google.com", sample_size=50 ):
        self.host = host
        self.pings = deque( [], sample_size )
        self.indexes = deque( [], sample_size )

        self.init_plot()

    def ping_host( self ):
        """
        Pings the host once and returns the latency.
        """
        # Works with both Windows and Linux
        os_arg = [ '-n' if  platform.system().lower() == 'windows' else '-c', '1' ]

        # Run the ping command and read stdout
        response = subprocess.run( [ 'ping', *os_arg, self.host ], capture_output=True ).stdout.decode( 'utf-8' )
        
        # Check if the pinging was succesfull
        if 'Reply from' in response:

            # As I am pinging the host once I just parse the average latency value
            # Replace Average with Minimum or Maximum if you want those values
            self.indexes.append( 1 if len( self.indexes ) == 0 else self.indexes[-1] + 1 )
            self.pings.append( int( response.split( 'Average = ' )[1].split( 'ms' )[0] ) )

    def init_plot( self ):
        """
        Creates the matplotlib figure and axes and starts the interactive plotting.
        """
        # Set plotting styles
        with plt.xkcd():
            plt.style.use( 'fivethirtyeight' )

            self.fig, self.ax = plt.subplots( 1, 1 )
            self.fig.set_figwidth( 12 )
            self.fig.set_figheight( 5 )

            self.ani = FuncAnimation( self.fig, self.step, interval=100 )
        
            plt.tight_layout()
            plt.show()

    def step( self, i ):
        """
        Pings the host, sets some drawing parameters and draws the line graph.
        """
        self.ping_host()

        # Clear the current axes
        plt.cla()

        # Adjust the plot a bit right so the Y label can fit
        plt.subplots_adjust( left=.07 )

        # Set the limits, labels, title and add units to the Y ticks
        self.ax.set_ylim( 0, max( self.pings )*1.5 )
        self.ax.set_xlabel( 'Index', fontweight='bold', fontsize=14 )
        self.ax.set_ylabel( 'Latency [ms]', fontweight='bold', fontsize=14 )
        self.ax.set_title( 'Ping Test (max:{}, min:{}, avg:{:.2f})'.format( max( self.pings ), min( self.pings ), sum( self.pings ) / len( self.pings ) ), fontweight='bold', fontsize=18 )
        self.ax.yaxis.set_major_formatter( mticker.FormatStrFormatter( '%d ms' ) )

        # Draw the lines
        plt.plot( self.indexes, self.pings, linewidth=1, marker='o', markersize=3, color='black' )


if __name__ == '__main__':
    p = PingTester()