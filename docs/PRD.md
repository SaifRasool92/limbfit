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
- **Reconstruction Accuracy:** Mean circumference error (in mm) compared to ground truth tape measurements.
- **Retrieval Quality:** Recall@5 (before and after fine-tuning the embedder on domain questions).
- **Generation Time:** End-to-end socket generation time (target: < 5 seconds).
- **Cost:** Estimated material cost per socket based on filament usage.

## 5. Non-Goals
- Bionic or powered hands (focus is strictly on the transradial socket).
- Full clinical validation or patient trials within the hackathon scope.
- Authentication, payments, or patient record databases.

## 6. Safety Statement
**Draft for prosthetist review.** This software produces a preliminary draft and is *not* a certified medical device. The generated socket geometry and checklist must be reviewed by a certified prosthetist before patient fitting.

## 7. Citations (TODO)
- [Placeholder for MDPI Safety 10(3):55]
- [Placeholder for PJMHS 2015 fodder cutter study]
- [Placeholder for University of Twente / Edge Hill studies on printed socket strength]
