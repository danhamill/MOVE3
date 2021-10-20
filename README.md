# MOVE3
Working dashboard for MOVE.3 streamflow record extension.

This application is designed to perform Bulletin 17C (England et al. 2019) record extenstion using MOVE.3 Methodologies.  There are three possible extenstion using the MOVE.3:
1. Full N2 extenstion - This provides the longest possible short record extension.  Be careful because this type of extension has the potienatl to be artifically long and could result in underestimation of uncertainity of the resutling flood frequency curve.

2. ne (mean) extenstion - This provides extension based upon the variance of the mean.  

3. ne (variance) extension - This providees the shortest possible short record exenstion using the variance of variance.  This type of extension is prefferable when uncertainity is primary concern.  Note: This is the preffered approach presented in Bulletin 17C

## Assumptions

Data are read into the applicaiton from a csv format with the following format:

| WY   | flow |
|------|------|
| 1900 | 3000 |
| 1901 | 5000 |

There should be a individual files for short and long records.  The files get merged into a single dataframe within the code. Example input is provided in `data/`

## References
- England, John F., Jr., Timothy A. Cohn, Beth A. Faber, Jery R. Stedinger, Wilbert O. Thomas Jr., Andrea G. Veilleux, Julie E. Kiang, and Robert R. Mason, Jr. 2019. “Guidelines for Determining Flood Flow Frequency—Bulletin 17C.” Techniques and Methods. US Geological Survey. https://doi.org/10.3133/tm4b5.
## Requirements

Tested on python 3.7

1. altair
2. sklearn
3. numpy
4. pandas
5. streamlit

## To run app
```
streamlit run .\ui_move.py
```
