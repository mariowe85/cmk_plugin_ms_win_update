# Checkmk Plugin: Microsoft Windows Update with SCCM Support

The **Microsoft Windows Update with SCCM Support** agent plugin is an enhanced extension for the monitoring software **Checkmk**.  
Originally created by Christopher Pommer and enhanced with SCCM support by Mario Fellner.  
It can be integrated into Checkmk 2.3 or newer and provides comprehensive monitoring of Windows updates from multiple sources.

You can download the extension package as an `.mkp` file from the [releases](../../releases) in this repository and upload it directly to your Checkmk site.  
See the Checkmk [documentation](https://docs.checkmk.com/latest/en/mkps.html) for details.

## What's New in Version 2.0

### 🆕 SCCM Integration
- **Full SCCM Support**: Monitor updates deployed through System Center Configuration Manager
- **SCCM Client Monitoring**: Track SCCM client service status, version, and policy updates
- **Dual-Source Monitoring**: Monitor both Windows Update and SCCM simultaneously
- **SCCM-Specific Metrics**: Evaluation states, deployment deadlines, compliance status

### 🔧 Enhanced Features
- **Multi-Source Thresholds**: Set different alert thresholds for Windows Update vs SCCM
- **Detailed Update Information**: KB articles, severity levels, download sizes, reboot requirements
- **Critical Update Alerting**: Special alerts for security-critical updates
- **Improved Filtering**: Advanced regex pattern matching for update exclusions
- **Enhanced Metrics**: Separate performance metrics for each update source

### 📊 Better Visualization
- **Source Breakdown Graphs**: Visualize updates by source (Windows Update vs SCCM)
- **Enhanced Perfometers**: Multi-segment performance indicators
- **Detailed Service Output**: Comprehensive update information in service details

## Plugin Information

This enhanced plugin provides monitoring for:

1. **Windows Update**: Traditional Microsoft Windows Update service
2. **SCCM Updates**: Updates deployed via System Center Configuration Manager
3. **SCCM Client**: Service status and health monitoring
4. **Update Details**: Comprehensive information about each pending update

See [Check Details](#check-details) for more information.

## Requirements

### For Windows Update Monitoring
- Windows Update service accessible
- PowerShell with WMI access
- Microsoft.Update.Session COM objects

### For SCCM Monitoring  
- SCCM client installed and configured
- CcmExec service running
- WMI access to ROOT\ccm namespace
- Proper SCCM client permissions

## Check Details

### Windows Update with SCCM Support

#### Description

This enhanced check monitors pending Windows updates from both Windows Update and SCCM sources. It provides:

- **Unified Monitoring**: Single service monitoring multiple update sources
- **Flexible Configuration**: Enable/disable individual sources as needed
- **Advanced Filtering**: Regex-based update exclusion patterns
- **Detailed Reporting**: Comprehensive update information and SCCM client status
- **Multiple Alert Levels**: Separate thresholds for total, Windows Update, and SCCM counts

#### Checkmk Service Examples

**Multi-Source Environment:**
```
Windows update OK - Total pending: 4, Windows Update pending: 2, SCCM pending: 2, Ignored: 1
SCCM client running (v5.00.9012.1000), last policy update: 2025-01-14 10:30:00
```

**SCCM-Only Environment:**
```
Windows update WARN - Total pending: 3, SCCM pending: 3 (!)
SCCM client running (v5.00.9012.1000), 1 critical/important updates pending
```

**Windows Update Only:**
```
Windows update OK - Total pending: 1, Windows Update pending: 1
```

#### Checkmk Parameters

1. **Total Pending Update Count**: Set upper thresholds for the combined count of pending updates from all sources. Default: 1 (WARN), 5 (CRIT).

2. **Windows Update Count**: Set separate thresholds specifically for Windows Update pending updates. Useful for environments where SCCM updates are managed differently.

3. **SCCM Update Count**: Set separate thresholds specifically for SCCM pending updates. Allows different alerting policies for SCCM vs Windows Update.

4. **Monitor SCCM Client Status**: Enable monitoring of the SCCM client service status and report warnings if the client is not running properly. Default: Enabled.

5. **Alert on Critical Updates**: Generate warnings when critical or important security updates are pending, regardless of count thresholds. Default: Disabled.

6. **Ignored Update Patterns**: Define regex patterns for updates to exclude from threshold calculations. Examples:
   - `Security Intelligence Update` (Defender definitions)
   - `KB1234567` (Specific KB articles)
   - `Definition Update` (All definition updates)

#### Agent Plugin Configuration

The agent plugin supports several configuration options:

- **Enable SCCM Monitoring**: Control whether SCCM updates are checked (default: enabled)
- **Enable Windows Update Monitoring**: Control whether Windows Update is checked (default: enabled)  
- **Execution Interval**: Configure how frequently the plugin runs (recommended: 5+ minutes)
- **Debug Mode**: Enable detailed logging for troubleshooting (default: disabled)

## Migration from Version 1.0

The enhanced version is designed to coexist with the original plugin during migration:

1. **New Agent Section**: Uses `ms_win_update_v2` section name to avoid conflicts
2. **New Check Plugin**: Deploys as `ms_win_update_v2` check
3. **Enhanced Rulesets**: New configuration options while maintaining familiar interface
4. **Backward Compatibility**: Original plugin continues working unchanged

### Migration Steps

1. Install the enhanced plugin package (`.mkp` file)
2. Configure the new bakery rule for `ms_win_update_v2`
3. Deploy the enhanced agent plugin to test hosts
4. Verify functionality and adjust parameters as needed
5. Gradually migrate remaining hosts
6. Remove the original plugin when migration is complete

## Performance Considerations

- **Execution Interval**: Set to 5+ minutes to avoid performance impact
- **Resource Usage**: SCCM WMI queries can be resource-intensive
- **Large Environments**: Consider staggered deployment in environments with many hosts
- **Debug Mode**: Disable in production to reduce overhead

## Troubleshooting

### Common Issues

1. **SCCM Updates Not Showing**: Verify SCCM client is running and WMI access is available
2. **Permission Errors**: Ensure Checkmk agent has proper WMI access rights
3. **High Resource Usage**: Increase execution interval or disable unused features
4. **Missing Updates**: Check update source configuration and filter patterns

### Debug Mode

Enable debug mode in the bakery configuration to get detailed logging information for troubleshooting issues.

## Support

For issues, feature requests, or contributions, please use the GitHub repository issue tracker.
