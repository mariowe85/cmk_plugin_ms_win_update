# Checkmk Plugin: Microsoft Windows Update

The **Microsoft Windows Update** agent plugin is an extension for the monitoring software **Checkmk**.  
It can be integrated into Checkmk 2.3 or newer.

You can download the extension package as an `.mkp` file from the [releases](../../releases) in this repository and upload it directly to your Checkmk site.  
See the Checkmk [documentation](https://docs.checkmk.com/latest/en/mkps.html) for details.

## Plugin Information

The Plugin provides monitoring for pending Windows updates.

See [Check Details](#check-details) for more information.

## Check Details

### Windows Update

#### Description

This check monitors the count of pending Windows updates.
It counts all Windoes updates which are not ignored.

#### Checkmk Service Examples

<img width="605" height="63" alt="grafik" src="https://github.com/user-attachments/assets/54d485a4-ef02-4930-aec1-52e0c2b9166c" />

<img width="792" height="62" alt="grafik" src="https://github.com/user-attachments/assets/0a38d4c3-99f8-48d8-9347-914814602e0d" />


#### Checkmk Parameters

1. **Pending Update Count**: Set upper thresholds for the count of pending Windows updates. All pending updates that have not been ignored in "Ignored Update Patterns" are counted. To ignore the pending update count completely, select "No levels". The default values are 1 (WARN) and 5 (CRIT). 
2. **Ignored Update Patterns**: Define a list of update names to be ignored for the pending update thresholds. The text entered here is handled as a regular expression pattern.

