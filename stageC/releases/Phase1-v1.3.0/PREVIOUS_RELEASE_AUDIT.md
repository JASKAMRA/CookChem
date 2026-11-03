# Historical release audit

The read-only verifier for the existing Stage C releases/Phase1B-v1.0.0 package returned FAIL during this update (1064 artifact entries; CHECKSUMS.json detached digest mismatch and listed-file hash/size mismatches). The historical directory was not modified or regenerated. This issue does not affect the separately built Phase1-v1.3.0 package; verify the new package independently with its own CHECKSUMS.json and CHECKSUMS.sha256.
