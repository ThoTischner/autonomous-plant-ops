# ArtifactHub Official-Status Request (draft)

This is the prepared request to be filed against
[`artifacthub/hub`](https://github.com/artifacthub/hub/issues/new?template=official-status-request.md)
using the **Official status request** template.

> **Prerequisite — must be satisfied before filing:** the repository must already
> show the **Verified Publisher** badge. That depends on ArtifactHub re-indexing the
> updated `helm/artifacthub-repo.yml` (with the restored `owners.email`) after it is
> published to the `gh-pages` branch by the Chart Release workflow. File this request
> only once the Verified Publisher badge is visible on the package page.

---

**Title:** `[OFFICIAL] autonomous-plant-ops`

- **Repository name** *(in `artifacthub.io`)*: `autonomous-plant-ops`
- **Official packages** *(leave empty if all packages in the repository are official)*: *(empty — the repository contains only the `autonomous-plant-ops` chart, which is official)*
- **Project URL:** https://github.com/ThoTischner/autonomous-plant-ops
- **Is the publisher a CNCF project? (graduated, incubating or sandbox):** No
- **Source code URL:** https://github.com/ThoTischner/autonomous-plant-ops
- **Other relevant URLs:**
  - Package: https://artifacthub.io/packages/helm/autonomous-plant-ops/autonomous-plant-ops
  - Chart README: https://github.com/ThoTischner/autonomous-plant-ops/blob/main/helm/autonomous-plant-ops/README.md
  - Signed OCI chart: `oci://ghcr.io/thotischner/charts/autonomous-plant-ops` (cosign keyless / Sigstore)

**Requirements checklist:**

- [x] The repository has already obtained the **Verified Publisher** status. *(verify on the live package page before filing)*
- [x] The user requesting the status is the publisher of the repository in Artifact Hub (`ThoTischner`, owner email `ai-solutions-camp@email.de`).
- [x] All official packages provide a `README.md` — see `helm/autonomous-plant-ops/README.md`.

**Justification:** The publisher (`ThoTischner`) is the author and sole owner of the
`autonomous-plant-ops` software that the chart deploys. The chart, all five container
images (`ghcr.io/thotischner/autonomous-plant-ops/*`) and the source code are published
from this same repository.
