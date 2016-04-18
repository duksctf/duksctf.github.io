---
layout: post
title: "Plaid CTF 2016 - Kriptovor"
date: 2016-04-15
---

*Kriptovor is a real ransomware, we analyzed the pcap, found the privatekey in
the second email send by the malware, we then installed Delphi and use the
lockbox3 library to decrypt with the RSA private key the AES key that was used
to encrypt the flag.*

<!--more-->

### Description

*HALP I GOT PWNED AND I DON'T HAVE BITCOINS*

*WARNING: this zip is password protected with the password "infected". The exe
file it has contains de-fanged malware (as does a later stage of the problem).* 

*This should not be active as is and will not infect your machine/encrypt your
files, but please be very very careful as this is based on real ransomware. It
is entirely possible to solve this without the exe files, but they are included
for completeness.*

### Details

Points:      300

Category:    Misc/Reverse/Crypto

Validations: 11

### Solution

We were given a file called [traffic.pcap](/resources/2016/pctf/kriptovor/traffic.pcap).
After digging around the file for a while it appears that it's a capture of the communication between the ransomware and his C&C.
We found the following [analysis](https://www.fireeye.com/blog/threat-research/2015/04/analysis_of_kriptovo.html) on google.
It's written that after successful infection, the ransomware will send three
files with SMTP:

* The list of the process running on the victim
* A screenshot of the desktop
* Private key used to encrypt AES key for encrypting the victim's files

We extracted the private key found in the second email:

<img src="/resources/2016/pctf/kriptovor/privkey.png" width="800">

After downloading, installing and updating the trial version of [Delphi 2010](https://www.embarcadero.com/fr/products/delphi/start-for-free).
We wrote a simple [Delphi Application](/resources/2016/pctf/kriptovor/code.delphi) to load the privkey that we extracted earlier and decrypt the [docx flag file](/resources/2016/pctf/kriptovor/flag.docx.just).

```
unit rsa;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.StdCtrls, uTPLb_Codec,
  uTPLb_CryptographicLibrary, uTPLb_BaseNonVisualComponent, uTPLb_Signatory;

type
  TForm2 = class(TForm)
    Button1: TButton;
    Button2: TButton;
    Signatory1: TSignatory;
    CryptographicLibrary1: TCryptographicLibrary;
    RSACodec: TCodec;
    Button3: TButton;
    Button4: TButton;
    Button5: TButton;
    procedure Button1Click(Sender: TObject);
    procedure Button2Click(Sender: TObject);
    procedure Button3Click(Sender: TObject);
    procedure Button4Click(Sender: TObject);
  private
    { Déclarations privées }
  public
    { Déclarations publiques }
  end;

var
  Form2: TForm2;

implementation

{$R *.dfm}
uses  uTPLb_StreamUtils, uTPLb_Constants, uTPLb_Asymetric, uTPLb_StrUtils;
procedure TForm2.Button1Click(Sender: TObject);
begin
Signatory1.GenerateKeys;
end;

procedure TForm2.Button2Click(Sender: TObject);
const sRSAKeyFileName = 'c:\rsa.key';
var
  Store: TFileStream;


begin
Store := TFileStream.Create(sRSAKeyFileName, fmCreate);
Store.Position := 0;

Signatory1.StoreKeysToStream( Store, [partPrivate] );
end;

procedure TForm2.Button3Click(Sender: TObject);
const sRSAKeyFileName = 'c:\jon\rsa.key';
const sEncryptedFile = 'c:\jon\aes_encrypted';
  var
  Store: TFileStream;
  Source: System.TArray<Byte>;
  s: String;
  Base64Store: TStream;
begin
Store := TFileStream.Create( sRSAKeyFileName, fmOpenRead);
try
  Store.Position := 0;
  Signatory1.LoadKeysFromStream( Store, [partPrivate]);
  Source := Stream_to_Base64( Store );
  Base64Store := TFileStream.Create( sRSAKeyFileName + 'b64', fmCreate );
  Base64Store.WriteBuffer( Source[1], Length( Source ) );
  Base64Store.Free;


finally
  Store.Free
  end
end;
procedure TForm2.Button4Click(Sender: TObject);
const sEncryptedFile = 'c:\jon\aes_encrypted';
const sDecryptedFile = 'c:\jon\aes_decrypted';
begin
RSACodec.DecryptFile(sDecryptedFile, sEncryptedFile);

end;
end.
```

After running our tool:

<img src="/resources/2016/pctf/kriptovor/privkey.png" width="800">

we were left with a shiny *aes_decrypted* file which is a docx file.

```bash
$ file aes_decrypted 
aes_decrypted: Microsoft Word 2007+
```
Opening the docx file gave us the flag: **PCTF{Th4t_w0uld_H4v3_b3en_2_B1tc01nz}**


Challenges resources are available in the [resources folder](https://github.com/duksctf/duksctf.github.io/tree/master/resources/2016/pctf/kriptovor).

