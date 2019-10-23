from dataclasses import dataclass


@dataclass
class MockedExtension:
    filename = "mocked_extension_0.1.0.vsix"
    created_time = "2018-08-08T14:14:02.212Z"
    modified_time = "2018-08-08T14:14:02.212Z"
    name = "mocked_extension"
    version = "0.1.0"
    publisher = "mocker"
    display_name = "Mocked Extension"
    properties = {
        "Microsoft.VisualStudio.Services.Branding.Color": "#1e415e"
    }
    tags = ["mocked", "extension"]
    license = "MIT"
    manifest = "{}"
    details = "This is a mocked extension details"
    description = "This is a mocked extension description"
