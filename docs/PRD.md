# LimbFit AI - Product Requirements Document (PRD)

## 1. Problem
In Punjab, agricultural machinery (such as fodder cutters "toka" and threshers) causes a large share of occupational injuries, predominantly upper-limb trauma in young workers. Imported prostheses are completely unaffordable. While 3D printing significantly lowers the material cost, customizing the prosthetic socket requires specialized CAD skills that rural clinics and technicians lack. The core bottleneck to affordable prosthetics in this region is **design expertise, not printing hardware.**

## 2. Target User
- **Rural Technician / TEVTA CAD Student:** They have access to a smartphone and a 3D printer, but no advanced clinical or CAD modeling expertise.

## 3. Core Flow
1. **Capture:** The user takes 2 photos (front and side) of the residual forearm, placing a printed reference marker of known size next to the limb.
2. **Measure:** The system automatically extracts scaled measurements (circumferences at multiple heights).
3. **Design:** The parametric geometry engine automatically designs a 3D printable transradial socket.
4. **Review & Output:** The system outputs an STL file for 3D printing and provides a cited checklist of clinical design rationale and fit guidance (bilingual: English/Urdu) for prosthetist review.

## 4. Success Metrics
- **Synthetic Geometry Reconstruction Consistency:** Mean circumference error (in mm) compared to target geometry.
- **Real Image Measurement Accuracy:** Mean measurement error (in mm) compared to ground truth tape measurements (requires manual test set).
- **Retrieval Quality:** Recall@5 (before and after fine-tuning the embedder on domain questions).
- **Generation Time:** End-to-end socket generation time (target: < 5 seconds).
- **Cost:** Estimated material cost per socket based on filament usage.

## 5. Non-Goals
- Bionic or powered hands (focus is strictly on the transradial socket).
- Full clinical validation or patient trials within the hackathon scope.
- Authentication, payments, or patient record databases.

## 6. Safety Statement
**Draft for prosthetist review.** This software produces a preliminary draft and is *not* a certified medical device. The generated socket geometry and checklist must be reviewed by a certified prosthetist before patient fitting.

## 7. Citations
- **MDPI Safety 10(3):55**: Iqbal, M. et al. "Agricultural Machinery Injuries in Rural Punjab: A Retrospective Analysis." *Safety* 2024, 10(3), 55. https://doi.org/10.3390/safety10030055
- **PJMHS 2015 Fodder Cutter Study**: Ahmad, A. et al. "Pattern of Fodder Cutter (Toka) Injuries in Rural Population." *Pakistan Journal of Medical and Health Sciences* 2015, 9(4), 1215-1218.
- **Printed Socket Strength**: Smit, G. et al. "Mechanical strength of 3D printed transradial prosthetic sockets." *Prosthetics and Orthotics International* 2021 (University of Twente / Edge Hill University collaborative study).
